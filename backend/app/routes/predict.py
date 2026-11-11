from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.scan import Scan
from app.services import risk_engine
from app.services.prediction_service import ModelNotReady, prediction_service
from app.utils.deps import get_session_id
from app.utils.images import validate_and_save
from app.utils.payload import scan_payload

router = APIRouter(prefix="/api", tags=["predict"])
CROPS = {"Tomato", "Potato", "Pepper"}


@router.post("/predict")
async def predict(
    file: UploadFile = File(...),
    crop: str | None = Form(default=None),
    temperature_c: float | None = Form(default=None, ge=-30, le=60),
    humidity_pct: float | None = Form(default=None, ge=0, le=100),
    rainfall_mm: float | None = Form(default=None, ge=0, le=1000),
    soil_moisture: float | None = Form(default=None, ge=0, le=1),
    latitude: float | None = Form(default=None, ge=-90, le=90),
    longitude: float | None = Form(default=None, ge=-180, le=180),
    db: Session = Depends(get_db),
    session_id: str | None = Depends(get_session_id),
):
    if crop and crop not in CROPS:
        raise HTTPException(422, f"crop must be one of {sorted(CROPS)} (or empty for auto).")
    name = validate_and_save(await file.read())
    try:
        result = await run_in_threadpool(prediction_service.predict, settings.uploads_dir / name)
    except ModelNotReady as e:
        (settings.uploads_dir / name).unlink(missing_ok=True)
        raise HTTPException(503, str(e))

    env = {"temperature_c": temperature_c, "humidity_pct": humidity_pct, "rainfall_mm": rainfall_mm,
           "soil_moisture": soil_moisture, "latitude": latitude, "longitude": longitude}
    risk = risk_engine.assess(temperature_c, humidity_pct, rainfall_mm, soil_moisture)
    scan = Scan(session_id=session_id, image_file=name, original_name=(file.filename or "")[:255], selected_crop=crop or None,
                predicted_class=result["predicted_class"], crop=result["crop"], is_healthy=result["is_healthy"],
                confidence=result["confidence"], top3=result["top3"], model_version=result["model_version"],
                environment=env if risk else None, risk=risk)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    payload = scan_payload(scan)
    payload["class_index"] = result["class_index"]
    return payload
