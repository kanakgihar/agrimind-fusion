"""Builds the one JSON shape used by /api/predict and /api/scans/{id} (the shared API contract)."""
from app.config import settings
from app.models.scan import Scan
from app.services import recommendation_service
from app.services.disease_knowledge import display_name
from app.services.prediction_service import NOTE


from datetime import timezone


def iso(dt):
    if dt is None:
        return None
    return (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt).isoformat()


def file_url(folder: str, name: str | None):
    return f"/files/{folder}/{name}" if name else None


def scan_payload(scan: Scan) -> dict:
    gi = scan.gradcam_info or {}
    warnings = []
    if scan.confidence < settings.low_conf:
        warnings.append(f"Low model confidence ({scan.confidence:.0%}). Treat this result as uncertain.")
    if scan.selected_crop and scan.selected_crop != scan.crop:
        warnings.append(f"You selected {scan.selected_crop} but the model predicts a {scan.crop} class.")
    rec = recommendation_service.build(scan.predicted_class, scan.confidence, scan.selected_crop, scan.risk, settings.low_conf)
    return {
        "scan_id": scan.id, "created_at": iso(scan.created_at),
        "predicted_class": scan.predicted_class, "display_name": display_name(scan.predicted_class),
        "crop": scan.crop, "selected_crop": scan.selected_crop, "is_healthy": scan.is_healthy,
        "confidence": scan.confidence, "top3": scan.top3, "model_version": scan.model_version,
        "low_confidence": scan.confidence < settings.low_conf, "warnings": warnings, "note": NOTE,
        "image_url": file_url("uploads", scan.image_file), "original_name": scan.original_name,
        "environment": scan.environment, "risk": scan.risk,
        "gradcam_info": gi or None,
        "gradcam_overlay_url": file_url("gradcam", gi.get("overlay")), "gradcam_heatmap_url": file_url("gradcam", gi.get("heatmap")),
        "recommendation": rec,
    }
