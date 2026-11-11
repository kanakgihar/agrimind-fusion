import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import assistant_service, recommendation_service, risk_engine  # noqa: E402
from app.services.disease_knowledge import KNOWLEDGE  # noqa: E402

CLASSES_15 = [
    "Pepper__bell___Bacterial_spot", "Pepper__bell___healthy", "Potato___Early_blight", "Potato___healthy",
    "Potato___Late_blight", "Tomato_Bacterial_spot", "Tomato_Early_blight", "Tomato_healthy", "Tomato_Late_blight",
    "Tomato_Leaf_Mold", "Tomato_Septoria_leaf_spot", "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot", "Tomato__Tomato_mosaic_virus", "Tomato__Tomato_YellowLeaf__Curl_Virus",
]


class TestRisk(unittest.TestCase):
    def test_none_when_empty(self):
        self.assertIsNone(risk_engine.assess())

    def test_high(self):
        r = risk_engine.assess(temperature_c=22, humidity_pct=92, rainfall_mm=20, soil_moisture=0.45)
        self.assertEqual(r["category"], "High")
        self.assertEqual(r["score"], 6)

    def test_low(self):
        r = risk_engine.assess(temperature_c=38, humidity_pct=30, rainfall_mm=0, soil_moisture=0.05)
        self.assertEqual(r["category"], "Low")
        self.assertTrue(r["stress_flags"])

    def test_partial_inputs(self):
        r = risk_engine.assess(humidity_pct=90)
        self.assertEqual(r["score"], 2)
        self.assertIn("rainfall_mm", r["missing_inputs"])

    def test_compare(self):
        c = risk_engine.compare({"temperature_c": 22, "humidity_pct": 50, "rainfall_mm": 0},
                                {"temperature_c": 22, "humidity_pct": 90, "rainfall_mm": 20})
        self.assertEqual(c["baseline"]["category"], "Low")
        self.assertEqual(c["scenario"]["category"], "High")
        self.assertTrue(any(d["factor"] == "Humidity" and d["change"] == 2 for d in c["factor_changes"]))


class TestKnowledge(unittest.TestCase):
    def test_all_15_classes_present(self):
        self.assertEqual(sorted(KNOWLEDGE), sorted(CLASSES_15))

    def test_recommendations_traceable(self):
        for c in CLASSES_15:
            rec = recommendation_service.build(c, 0.9)
            self.assertTrue(rec["items"])
            for it in rec["items"]:
                self.assertTrue(it["source"] and it["why"])

    def test_low_confidence_and_crop_mismatch(self):
        rec = recommendation_service.build("Tomato_Late_blight", 0.4, selected_crop="Potato")
        self.assertEqual(len(rec["warnings"]), 2)

    def test_urgency_bump(self):
        risk = risk_engine.assess(temperature_c=20, humidity_pct=95, rainfall_mm=20)
        rec = recommendation_service.build("Tomato_Early_blight", 0.9, risk=risk)
        self.assertEqual(rec["urgency"], "high")

    def test_no_dose_text(self):
        import re
        for k in KNOWLEDGE.values():
            txt = " ".join(k["management"] + k["prevention"] + k["monitoring"])
            self.assertIsNone(re.search(r"\d+\s?(ml|g|kg|l)\b|per litre|per liter", txt, re.I))


class TestAssistant(unittest.TestCase):
    def test_ndvi(self):
        self.assertIn("B8", assistant_service.reply("what is ndvi?")["reply"])

    def test_context_followup(self):
        scan = {"predicted_class": "Tomato_Late_blight", "confidence": 0.9}
        r = assistant_service.reply("how do I prevent it?", scan)
        self.assertIn("Prevention", r["reply"])

    def test_named_disease(self):
        r = assistant_service.reply("tell me about potato late blight")
        self.assertIn("Potato", r["reply"])

    def test_unknown(self):
        r = assistant_service.reply("who won the cricket match", {"predicted_class": None, "confidence": 0.9})
        self.assertIn("do not have", r["reply"])


if __name__ == "__main__":
    unittest.main()
