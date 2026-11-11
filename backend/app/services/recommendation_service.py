"""Traceable recommendation engine: every item says which input produced it."""
from app.services import risk_engine
from app.services.disease_knowledge import (DISCLAIMER, KNOWLEDGE_SOURCE, display_name, get_knowledge)

URGENCY_ORDER = ["low", "moderate", "high"]


def _bump(level: str) -> str:
    return URGENCY_ORDER[min(URGENCY_ORDER.index(level) + 1, 2)]


def build(predicted_class: str, confidence: float, selected_crop: str | None = None,
          risk: dict | None = None, low_conf_threshold: float = 0.60) -> dict:
    k = get_knowledge(predicted_class)
    items = []
    warnings = []

    def add(section, text, source, why):
        items.append({"section": section, "text": text, "source": source, "why": why})

    if k is None:
        return {"urgency": "unknown", "summary": "No knowledge entry exists for this class.", "items": [],
                "warnings": ["Unknown class"], "knowledge_source": KNOWLEDGE_SOURCE, "disclaimer": DISCLAIMER}

    name = display_name(predicted_class)
    urgency = k["urgency"]
    low = confidence < low_conf_threshold
    if low:
        warnings.append(f"Low model confidence ({confidence:.0%}). Treat this result as uncertain.")
        add("Next step", "Retake the photo (single leaf, good daylight, in focus) and scan again before acting.",
            "model confidence", f"confidence {confidence:.0%} is below {low_conf_threshold:.0%}")
        add("Next step", "If symptoms are spreading, show the plant to a local agricultural officer instead of relying on this result.",
            "model confidence", "low-confidence predictions can be wrong")
    if selected_crop and selected_crop.lower() not in ("", "auto") and selected_crop != k["crop"]:
        warnings.append(f"You selected {selected_crop} but the model predicts a {k['crop']} class. Check the crop and the photo.")

    for t in k["management"]:
        add("Management", t, f"disease knowledge: {name}", f"model predicted {name}")
    for t in k["prevention"]:
        add("Prevention", t, f"disease knowledge: {name}", f"model predicted {name}")
    for t in k["monitoring"]:
        add("Monitoring", t, f"disease knowledge: {name}", f"model predicted {name}")

    if risk:
        cat = risk["category"]
        by = {f["factor"]: f for f in risk["factors"]}
        if cat == "High" and k["category"] != "healthy":
            urgency = _bump(urgency)
        if k["category"] in ("fungal", "oomycete", "bacterial") and cat in ("Moderate", "High"):
            add("Environmental precaution", "Weather currently favours leaf diseases: avoid overhead irrigation, keep foliage dry and improve airflow.",
                "rule-based environmental assessment", f"risk category is {cat} (score {risk['score']}/{risk['max_score']})")
        if by.get("Rainfall", {}).get("points", 0) >= 1 and k["category"] != "healthy":
            add("Irrigation", "Skip or reduce irrigation when rain is falling, and avoid wetting leaves.",
                "rule-based environmental assessment", by["Rainfall"]["explanation"])
        if k["category"] == "pest":
            for s in risk.get("stress_flags", []):
                add("Environmental precaution", "Hot, dry weather can encourage mites; check leaf undersides more often.",
                    "rule-based environmental assessment", s)
        for s in risk.get("stress_flags", []):
            if s.startswith("Dry soil"):
                add("Irrigation", "Soil looks dry: plan irrigation based on crop stage and local advice.",
                    "rule-based environmental assessment", s)
    else:
        add("Environmental precaution", "No weather data was provided, so no weather-based advice is included. Add temperature/humidity/rain to get it.",
            "missing input", "environment fields were empty")

    if k["category"] == "healthy":
        summary = f"{name}: no action needed beyond routine scouting."
    else:
        summary = f"{name}: urgency {urgency}. {k['summary']}"
    return {"urgency": urgency, "summary": summary, "category": k["category"], "items": items,
            "warnings": warnings, "knowledge_source": KNOWLEDGE_SOURCE, "disclaimer": DISCLAIMER}
