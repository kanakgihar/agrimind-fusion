from fastapi import APIRouter

from app.services.prediction_service import prediction_service

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health():
    st = prediction_service.status()
    st["model_ready"] = st["model_file_exists"] and st["class_names_exist"]
    return {"status": "ok", **st}
