"""Simulator, recommendations, chat, satellite - small stateless endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.scan import Scan
from app.schemas.schemas import ChatRequest, RecommendationRequest, SatelliteRequest, SimulatorRequest
from app.services import assistant_service, recommendation_service, risk_engine, satellite_service
from app.services.disease_knowledge import KNOWLEDGE
from app.utils.deps import get_session_id
from app.utils.payload import scan_payload

router = APIRouter(prefix="/api", tags=["tools"])


@router.post("/simulator")
def simulator(req: SimulatorRequest):
    try:
        return risk_engine.compare(req.baseline.model_dump(), req.scenario.model_dump())
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.post("/recommendations")
def recommendations(req: RecommendationRequest):
    if req.predicted_class not in KNOWLEDGE:
        raise HTTPException(422, "Unknown predicted_class. Use one of the names in models/class_names.json.")
    risk = risk_engine.assess(**req.environment.model_dump()) if req.environment else None
    return recommendation_service.build(req.predicted_class, req.confidence, req.selected_crop, risk, settings.low_conf)


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db), session_id: str | None = Depends(get_session_id)):
    scan = None
    if req.scan_id is not None:
        s = db.get(Scan, req.scan_id)
        if not s or (session_id and s.session_id not in (None, session_id)):
            raise HTTPException(404, "Scan not found.")
        scan = scan_payload(s)
    return assistant_service.reply(req.message, scan, [m.model_dump() for m in req.history])


@router.get("/satellite/status")
def satellite_status():
    return satellite_service.status()


@router.post("/satellite/indices")
async def satellite_indices(req: SatelliteRequest):
    try:
        return await run_in_threadpool(satellite_service.indices, req.latitude, req.longitude, req.start_date,
                                       req.end_date, req.radius_m, req.max_cloud_pct)
    except satellite_service.SatelliteUnavailable as e:
        raise HTTPException(503, str(e))
    except Exception as e:  # noqa: BLE001  (Earth Engine raises many types)
        raise HTTPException(502, f"Earth Engine request failed: {e}")
