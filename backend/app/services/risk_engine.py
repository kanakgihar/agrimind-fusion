"""Rule-based environmental risk engine (documented, explainable, NOT a trained model).

What it does: counts how many weather conditions are commonly associated with foliar-disease pressure
(leaf wetness, humidity, rain) or crop stress (heat, drought, waterlogging) and explains each point it awards.
What it does NOT do: identify a disease, or change the image model's prediction. Thresholds are generic
rules of thumb that you can adjust in RULES; they have not been validated against disease outcomes.
"""

RULE_VERSION = "rules-v1"

RULES = {
    "humidity": {"high": 85, "moderate": 70},          # % relative humidity
    "temperature_band": (15, 28),                      # deg C where many foliar pathogens are active
    "heat_stress": 35,                                 # deg C
    "rain_heavy": 15, "rain_some": 5,                  # mm per day
    "soil_wet": 0.40, "soil_dry": 0.10,                # m3/m3 volumetric soil moisture
}
CATEGORIES = [(0, "Low"), (2, "Moderate"), (4, "High")]
MAX_SCORE = 6


def _category(score: int) -> str:
    name = "Low"
    for lo, label in CATEGORIES:
        if score >= lo:
            name = label
    return name


def assess(temperature_c=None, humidity_pct=None, rainfall_mm=None, soil_moisture=None) -> dict | None:
    """Return an explained assessment, or None when no input was provided."""
    inputs = {"temperature_c": temperature_c, "humidity_pct": humidity_pct,
              "rainfall_mm": rainfall_mm, "soil_moisture": soil_moisture}
    missing = [k for k, v in inputs.items() if v is None]
    if len(missing) == len(inputs):
        return None

    r = RULES
    factors = []

    def add(name, points, value, text):
        factors.append({"factor": name, "points": points, "value": value, "explanation": text})

    if humidity_pct is not None:
        if humidity_pct >= r["humidity"]["high"]:
            add("Humidity", 2, humidity_pct, f"{humidity_pct:g}% is very humid (>= {r['humidity']['high']}%): leaves stay wet longer, which favours many fungal and bacterial leaf diseases.")
        elif humidity_pct >= r["humidity"]["moderate"]:
            add("Humidity", 1, humidity_pct, f"{humidity_pct:g}% is moderately humid (>= {r['humidity']['moderate']}%).")
        else:
            add("Humidity", 0, humidity_pct, f"{humidity_pct:g}% is below {r['humidity']['moderate']}%, so humidity is not adding disease pressure.")
    if temperature_c is not None:
        lo, hi = r["temperature_band"]
        if lo <= temperature_c <= hi:
            add("Temperature", 1, temperature_c, f"{temperature_c:g} C is inside {lo}-{hi} C, a range where many foliar pathogens are active.")
        else:
            add("Temperature", 0, temperature_c, f"{temperature_c:g} C is outside {lo}-{hi} C, so it adds no disease-pressure point.")
    if rainfall_mm is not None:
        if rainfall_mm >= r["rain_heavy"]:
            add("Rainfall", 2, rainfall_mm, f"{rainfall_mm:g} mm/day is heavy rain: splash spreads pathogens and prolongs leaf wetness.")
        elif rainfall_mm >= r["rain_some"]:
            add("Rainfall", 1, rainfall_mm, f"{rainfall_mm:g} mm/day is noticeable rain.")
        else:
            add("Rainfall", 0, rainfall_mm, f"{rainfall_mm:g} mm/day is little or no rain.")
    if soil_moisture is not None:
        if soil_moisture >= r["soil_wet"]:
            add("Soil moisture", 1, soil_moisture, f"{soil_moisture:g} m3/m3 is very wet soil: waterlogging stresses roots and favours some soil-borne problems.")
        else:
            add("Soil moisture", 0, soil_moisture, f"{soil_moisture:g} m3/m3 is not waterlogged.")

    score = sum(f["points"] for f in factors)

    stress = []
    if temperature_c is not None and temperature_c >= r["heat_stress"]:
        stress.append(f"Heat stress possible: {temperature_c:g} C is at or above {r['heat_stress']} C.")
    if soil_moisture is not None and soil_moisture <= r["soil_dry"]:
        stress.append(f"Dry soil: {soil_moisture:g} m3/m3 is at or below {r['soil_dry']}; consider irrigation planning.")
    if temperature_c is not None and rainfall_mm is not None and humidity_pct is not None \
            and temperature_c >= 30 and humidity_pct < 50 and rainfall_mm < 1:
        stress.append("Hot, dry and rain-free conditions: conditions where spider mites and water stress become more likely.")

    return {
        "category": _category(score), "score": score, "max_score": MAX_SCORE,
        "type": "rule-based assessment", "rule_version": RULE_VERSION,
        "inputs": inputs, "missing_inputs": missing, "factors": factors, "stress_flags": stress,
        "disclaimer": "Rule-based environmental context only. It does not diagnose disease and never changes the image model's prediction.",
    }


def compare(baseline: dict, scenario: dict) -> dict:
    """What-if comparison used by the simulator."""
    a, b = assess(**baseline), assess(**scenario)
    if a is None or b is None:
        raise ValueError("Provide at least one variable in both baseline and scenario.")
    a_pts = {f["factor"]: f["points"] for f in a["factors"]}
    b_pts = {f["factor"]: f["points"] for f in b["factors"]}
    names = sorted(set(a_pts) | set(b_pts), key=lambda n: ["Humidity", "Temperature", "Rainfall", "Soil moisture"].index(n))
    diffs = [{"factor": n, "baseline_points": a_pts.get(n, 0), "scenario_points": b_pts.get(n, 0),
              "change": b_pts.get(n, 0) - a_pts.get(n, 0)} for n in names]
    drivers = [d["factor"] for d in diffs if d["change"] != 0]
    if a["category"] == b["category"] and not drivers:
        summary = f"No change: risk stays {b['category']}."
    elif drivers:
        summary = f"Risk goes from {a['category']} to {b['category']} (score {a['score']} -> {b['score']}). Changed factors: {', '.join(drivers)}."
    else:
        summary = f"Risk stays {b['category']}."
    return {"baseline": a, "scenario": b, "factor_changes": diffs, "summary": summary,
            "label": "Rule-based scenario simulation. The image prediction is not recalculated."}
