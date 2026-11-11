
import os
import sys
import tempfile
import types
import unittest

from datetime import date, timedelta


# Add backend directory to Python path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..")
)


# Allow running tests without httpx installed
try:
    import httpx  # noqa: F401

except ImportError:
    stub = types.ModuleType("httpx")

    stub.HTTPError = type("HTTPError", (Exception,), {})

    stub.HTTPStatusError = type(
        "HTTPStatusError",
        (stub.HTTPError,),
        {}
    )

    sys.modules["httpx"] = stub


from app.services import (
    recommendation_service,
    report_service,
    risk_engine,
    weather_service,
)


class TestReport(unittest.TestCase):

    def test_pdf_builds(self):

        from PIL import Image

        with tempfile.TemporaryDirectory() as d:

            p = os.path.join(d, "leaf.jpg")

            Image.new(
                "RGB",
                (300, 200),
                (30, 120, 40)
            ).save(p)

            risk = risk_engine.assess(
                temperature_c=22,
                humidity_pct=90,
                rainfall_mm=10
            )

            rec = recommendation_service.build(
                "Tomato_Late_blight",
                0.93,
                "Tomato",
                risk
            )

            scan = {
                "scan_id": 7,
                "created_at": "2026-11-01",
                "display_name": "Tomato - Late blight",
                "crop": "Tomato",
                "is_healthy": False,
                "confidence": 0.93,
                "model_version": "mobilenetv2_final",

                "top3": [
                    {
                        "display_name": "Tomato - Late blight",
                        "confidence": 0.93
                    }
                ],

                "warnings": [],

                "gradcam_info": {
                    "main_region": "central",
                    "coverage_pct": 22.5
                },

                "environment": risk["inputs"],
                "risk": risk,
            }

            pdf = report_service.build_pdf(
                scan,
                rec,
                p,
                p
            )

            self.assertTrue(pdf.startswith(b"%PDF"))
            self.assertGreater(len(pdf), 3000)

            with open("/tmp/sample_report.pdf", "wb") as f:
                f.write(pdf)


class TestWeatherParsing(unittest.TestCase):

    def test_forecast_parsing(self):

        hours = [
            f"2026-11-0{d}T{h:02d}:00"
            for d in (1, 2)
            for h in range(24)
        ]

        fake = {
            "latitude": 26.8,
            "longitude": 80.9,
            "timezone": "Asia/Kolkata",

            "current": {
                "time": "2026-11-01T14:30",
                "temperature_2m": 30.1,
                "relative_humidity_2m": 55,
                "precipitation": 0,
                "rain": 0,
                "wind_speed_10m": 6.2,
            },

            "hourly": {
                "time": hours,
                "relative_humidity_2m": [50] * 24 + [80] * 24,
                "soil_moisture_3_to_9cm": [0.2] * 24 + [0.3] * 24,
            },

            "daily": {
                "time": ["2026-11-01", "2026-11-02"],
                "temperature_2m_max": [32, 30],
                "temperature_2m_min": [18, 17],
                "precipitation_sum": [0, 4],
                "rain_sum": [0, 4],
                "wind_speed_10m_max": [12, 10],
            },
        }

        original_get = weather_service._get

        weather_service._get = lambda url, params: fake

        try:
            out = weather_service.forecast(26.8, 80.9)

        finally:
            weather_service._get = original_get

        self.assertEqual(
            out["current"]["soil_moisture"],
            0.2
        )

        self.assertEqual(
            out["daily"][1]["humidity_mean"],
            80
        )

        self.assertEqual(
            out["daily"][0]["temp_mean"],
            25.0
        )


    def test_history_rejects_recent_and_long(self):

        # Test 1: Reject a historical range longer than 92 days.
        with self.assertRaises(weather_service.WeatherError):

            weather_service.history(
                0,
                0,
                "2020-01-01",
                "2020-12-31"
            )

        # Test 2: Reject recent dates dynamically.
        recent_date = date.today() - timedelta(days=1)

        start_date = recent_date - timedelta(days=10)

        with self.assertRaises(weather_service.WeatherError):

            weather_service.history(
                0,
                0,
                start_date.isoformat(),
                recent_date.isoformat()
            )


if __name__ == "__main__":
    unittest.main()
