"""AgriAI Assistant - rule-based fallback (no external LLM, no API key needed).

It answers only from the project's knowledge base and the current scan context, and says so when it cannot answer.
To plug in an LLM later, keep the same reply() signature and read the key from an environment variable in the backend.
"""
import re

from app.services.disease_knowledge import DISCLAIMER, KNOWLEDGE, display_name, get_knowledge

EXPLAIN = {
    "ndvi": "NDVI (Normalized Difference Vegetation Index) = (NIR - Red) / (NIR + Red), using Sentinel-2 bands B8 and B4. Higher values usually mean denser, greener vegetation; low values suggest bare soil, sparse or stressed vegetation. It is a vegetation indicator, not a disease diagnosis, and it describes a field area, not a single leaf.",
    "ndmi": "NDMI (Normalized Difference Moisture Index) = (NIR - SWIR) / (NIR + SWIR), using Sentinel-2 bands B8 and B11. It reflects canopy water content: higher values suggest more moisture in vegetation. It is a moisture indicator, not a disease diagnosis.",
    "gradcam": "Grad-CAM colours the image regions that most increased the model's score for the predicted class (red = stronger influence). It shows where the model looked; it does not prove the biological cause. If it highlights the background instead of the leaf, be sceptical of the prediction.",
    "confidence": "The confidence shown is the model's softmax output for a class. It is not a calibrated probability: a 95% score does not mean a 95% chance of being right, especially on photos unlike the training data (PlantVillage uses plain-background lab photos).",
    "weather": "The risk level is rule-based: points are added for high humidity, temperatures in a 15-28 C band, rainfall, and wet soil. It describes conditions that commonly favour leaf diseases; it does not tell you which disease is present, and it never changes the image prediction.",
    "limits": DISCLAIMER,
}


def _find_class(text: str, context_class: str | None):
    t = text.lower()
    for cls, k in KNOWLEDGE.items():
        key = k["display_name"].lower().split(" - ")[-1]
        if key in t and k["crop"].lower() in t:
            return cls
    for cls, k in KNOWLEDGE.items():
        key = k["display_name"].lower().split(" - ")[-1]
        if key in t and key != "healthy":
            return cls
    return context_class


def reply(message: str, scan: dict | None = None, history: list | None = None) -> dict:
    t = message.lower().strip()
    ctx_class = scan.get("predicted_class") if scan else None
    cls = _find_class(t, ctx_class)
    topic = None

    def done(text, topic):
        return {"reply": text, "topic": topic, "mode": "rule-based (no LLM configured)"}

    if re.search(r"\bndvi\b", t):
        return done(EXPLAIN["ndvi"], "ndvi")
    if re.search(r"\bndmi\b", t):
        return done(EXPLAIN["ndmi"], "ndmi")
    if re.search(r"grad[- ]?cam|heat ?map|highlight", t):
        extra = ""
        if scan and scan.get("gradcam_info"):
            extra = f" For your scan, the model attended mostly to the {scan['gradcam_info'].get('main_region', 'central')} region."
        return done(EXPLAIN["gradcam"] + extra, "gradcam")
    if re.search(r"confidence|softmax|probab|how sure|accura", t):
        extra = f" Your scan's score was {scan['confidence']:.0%}." if scan else ""
        return done(EXPLAIN["confidence"] + extra, "confidence")
    if re.search(r"humid|weather|rain|temperature|risk|moisture", t):
        extra = ""
        if scan and scan.get("risk"):
            extra = f" For your scan the rule-based risk was {scan['risk']['category']} (score {scan['risk']['score']}/{scan['risk']['max_score']})."
        return done(EXPLAIN["weather"] + extra, "weather")
    if re.search(r"limit|trust|reliab|field photo|real[- ]world|accurate", t):
        return done(EXPLAIN["limits"], "limits")

    k = get_knowledge(cls) if cls else None
    if k:
        name = display_name(cls)
        if re.search(r"prevent|avoid|stop it", t):
            return done(f"Prevention for {name}:\n- " + "\n- ".join(k["prevention"]), cls)
        if re.search(r"treat|cure|manage|what (should|can) i do|spray|fix|control|medicine|pesticide|fungicide", t):
            return done(f"General management for {name} (no doses given on purpose; check labels and local advice):\n- "
                        + "\n- ".join(k["management"]) + "\n\nI cannot guarantee any outcome.", cls)
        if re.search(r"monitor|watch|check|scout", t):
            return done(f"Monitoring for {name}:\n- " + "\n- ".join(k["monitoring"]), cls)
        return done(f"{name}: {k['summary']}", cls)

    if scan is None:
        return done("I can explain crop diseases from the 15 trained classes, Grad-CAM, confidence scores, the weather risk rules, NDVI and NDMI. "
                    "Select a scan or name a disease (for example 'tomato late blight').", None)
    return done("I do not have information on that. Try asking about the predicted disease, prevention, management, "
                "monitoring, Grad-CAM, confidence, weather risk, NDVI or NDMI.", None)
