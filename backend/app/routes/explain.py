from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.scan import Scan
from app.services import gradcam_service
from app.services.prediction_service import ModelNotReady, prediction_service
from app.utils.deps import get_session_id
from app.utils.payload import scan_payload

router = APIRouter(prefix="/api", tags=["explain"])
TEXT = ("Grad-CAM highlights image regions that increased the model's score for the predicted class. "
        "It shows where the model looked; it does not prove the biological cause of a disease.")


def _generate(scan: Scan) -> dict:
    model = prediction_service.model
    classes = prediction_service.classes
    idx = classes.index(scan.predicted_class)
    x = prediction_service.preprocess(settings.uploads_dir / scan.image_file)
    stem = f"scan{scan.id}"
    overlay, heat = f"{stem}_overlay.jpg", f"{stem}_heatmap.jpg"
    info = gradcam_service.generate(model, idx, x, settings.uploads_dir / scan.image_file,
                                    settings.gradcam_dir / overlay, settings.gradcam_dir / heat)
    return {**info, "overlay": overlay, "heatmap": heat, "original": f"{stem}_original.jpg"}


@router.get("/explain/{scan_id}")
async def explain(scan_id: int, db: Session = Depends(get_db), session_id: str | None = Depends(get_session_id)):
    scan = db.get(Scan, scan_id)
    if not scan or (session_id and scan.session_id not in (None, session_id)):
        raise HTTPException(404, "Scan not found.")
    if not scan.gradcam_info or not (settings.gradcam_dir / scan.gradcam_info.get("overlay", "")).exists():
        try:
            info = await run_in_threadpool(_generate, scan)
        except ModelNotReady as e:
            raise HTTPException(503, str(e))
        except gradcam_service.GradCamUnsupported as e:
            raise HTTPException(501, str(e))
        scan.gradcam_info = info
        db.commit()
    p = scan_payload(scan)
    return {"scan_id": scan.id, "display_name": p["display_name"], "confidence": p["confidence"],
            "gradcam_info": p["gradcam_info"], "original_url": p["image_url"],
            "overlay_url": p["gradcam_overlay_url"], "heatmap_url": p["gradcam_heatmap_url"], "explanation": TEXT}
