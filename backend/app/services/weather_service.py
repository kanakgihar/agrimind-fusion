
"""Open-Meteo weather service.

No API key required.
Responses are cached for 10 minutes.
Weather observations and forecasts are NEVER inputs to the image model.
"""

import time
from datetime import date, timedelta
from collections import defaultdict

import httpx


GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

TTL = 600
_cache: dict = {}


class WeatherError(Exception):
    """Raised when weather data cannot be retrieved or validated."""
    pass


def _get(url: str, params: dict) -> dict:
    """Fetch API data with a 10-minute in-memory cache."""

    key = (url, tuple(sorted(params.items())))
    hit = _cache.get(key)

    if hit and time.time() - hit[0] < TTL:
        return hit[1]

    try:
        response = httpx.get(url, params=params, timeout=15.0)
        response.raise_for_status()
        data = response.json()

    except httpx.HTTPStatusError as exc:
        raise WeatherError(
            f"Open-Meteo returned {exc.response.status_code}: "
            f"{exc.response.text[:200]}"
        ) from exc

    except (httpx.HTTPError, ValueError) as exc:
        raise WeatherError(
            f"Could not reach Open-Meteo: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise WeatherError("Invalid response received from Open-Meteo.")

    _cache[key] = (time.time(), data)

    return data


def geocode(query: str) -> list:
    """Convert a location name into geographic coordinates."""

    if not query or not query.strip():
        raise WeatherError("Please enter a valid location.")

    data = _get(
        GEO_URL,
        {
            "name": query.strip(),
            "count": 5,
            "language": "en",
            "format": "json",
        },
    )

    results = []

    for item in data.get("results", []):
        results.append({
            "name": item.get("name"),
            "admin1": item.get("admin1"),
            "country": item.get("country"),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
        })

    return results


def _mean(values):
    """Calculate the mean while ignoring missing values."""

    valid = [x for x in values if x is not None]

    if not valid:
        return None

    return round(sum(valid) / len(valid), 3)


def _daily_from_hourly(times, series: dict) -> dict:
    """Group hourly weather values by YYYY-MM-DD."""

    days = defaultdict(lambda: defaultdict(list))

    for i, timestamp in enumerate(times):

        day = timestamp[:10]

        for name, values in series.items():

            if values is not None and i < len(values):
                days[day][name].append(values[i])

    return days


def forecast(lat: float, lon: float) -> dict:
    """Get current weather and a 7-day forecast."""

    data = _get(
        FORECAST_URL,
        {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "forecast_days": 7,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "rain,"
                "wind_speed_10m"
            ),

            "hourly": (
                "relative_humidity_2m,"
                "soil_moisture_3_to_9cm"
            ),

            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_sum,"
                "rain_sum,"
                "wind_speed_10m_max"
            ),
        },
    )

    current = data.get("current") or {}
    hourly = data.get("hourly") or {}
    daily_data = data.get("daily") or {}

    times = hourly.get("time", [])

    # Find current-hour soil moisture.
    soil_now = None

    if current.get("time") and times:

        hour_key = current["time"][:13] + ":00"

        try:
            index = times.index(hour_key)

            soil_values = hourly.get(
                "soil_moisture_3_to_9cm", []
            )

            if index < len(soil_values):
                soil_now = soil_values[index]

        except ValueError:
            soil_now = None

    # Aggregate hourly humidity and soil moisture.
    humidity_by_day = _daily_from_hourly(
        times,
        {
            "rh": hourly.get("relative_humidity_2m", []),
            "soil": hourly.get(
                "soil_moisture_3_to_9cm", []
            ),
        },
    )

    # Build daily forecast.
    daily = []

    dates = daily_data.get("time", [])

    for i, day in enumerate(dates):

        def get_value(key):
            values = daily_data.get(key, [])
            return values[i] if i < len(values) else None

        temp_max = get_value("temperature_2m_max")
        temp_min = get_value("temperature_2m_min")

        temp_mean = None

        if temp_max is not None and temp_min is not None:
            temp_mean = round(
                (temp_max + temp_min) / 2, 1
            )

        daily.append({
            "date": day,
            "temp_max": temp_max,
            "temp_min": temp_min,
            "temp_mean": temp_mean,

            "precipitation_mm": get_value(
                "precipitation_sum"
            ),

            "rain_mm": get_value("rain_sum"),

            "wind_max_kmh": get_value(
                "wind_speed_10m_max"
            ),

            "humidity_mean": _mean(
                humidity_by_day[day]["rh"]
            ),

            "soil_moisture_mean": _mean(
                humidity_by_day[day]["soil"]
            ),
        })

    return {
        "location": {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
        },

        "current": {
            "time": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get(
                "relative_humidity_2m"
            ),
            "precipitation_mm": current.get(
                "precipitation"
            ),
            "rain_mm": current.get("rain"),
            "wind_kmh": current.get("wind_speed_10m"),

            "soil_moisture": soil_now,

            "soil_moisture_note": (
                "Volumetric soil moisture at 3-9 cm depth. "
                "Model estimate, not a field sensor. "
                "May be null."
            ),
        },

        "daily": daily,

        "source": "Open-Meteo forecast API",
    }


def history(
    lat: float,
    lon: float,
    start: str,
    end: str
) -> dict:
    """Get historical weather data for a maximum of 92 days."""

    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)

    except (ValueError, TypeError) as exc:
        raise WeatherError(
            "Invalid date. Use YYYY-MM-DD format."
        ) from exc

    if end_date < start_date:
        raise WeatherError(
            "End date is before start date."
        )

    if (end_date - start_date).days > 92:
        raise WeatherError(
            "Please choose a range of 92 days or less."
        )

    cutoff_date = date.today() - timedelta(days=2)

    if end_date >= cutoff_date:
        raise WeatherError(
            "Archive data is only available up to about "
            "2 days ago. Choose an earlier end date."
        )

    data = _get(
        ARCHIVE_URL,
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": start,
            "end_date": end,
            "timezone": "auto",

            "hourly": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation"
            ),
        },
    )

    hourly = data.get("hourly") or {}

    days = _daily_from_hourly(
        hourly.get("time", []),
        {
            "t": hourly.get("temperature_2m", []),
            "rh": hourly.get(
                "relative_humidity_2m", []
            ),
            "p": hourly.get("precipitation", []),
        },
    )

    output = []

    for day in sorted(days):

        precipitation = [
            value
            for value in days[day]["p"]
            if value is not None
        ]

        temperature_mean = _mean(days[day]["t"])
        humidity_mean = _mean(days[day]["rh"])

        output.append({
            "date": day,

            "temp_mean": (
                round(temperature_mean, 1)
                if temperature_mean is not None
                else None
            ),

            "humidity_mean": (
                round(humidity_mean, 1)
                if humidity_mean is not None
                else None
            ),

            "precipitation_mm": (
                round(sum(precipitation), 1)
                if precipitation
                else None
            ),
        })

    return {
        "daily": output,
        "start": start,
        "end": end,
        "source": "Open-Meteo archive API",
    }
