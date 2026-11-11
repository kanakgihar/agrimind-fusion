from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.scan import Scan
from app.services.disease_knowledge import display_name
from app.utils.deps import get_session_id
from app.utils.payload import file_url, iso, scan_payload

router = APIRouter(prefix="/api/scans", tags=["scans"])
SORTS = {"date_desc": Scan.created_at.desc(), "date_asc": Scan.created_at.asc(),
         "conf_desc": Scan.confidence.desc(), "conf_asc": Scan.confidence.asc()}


def _own(db: Session, scan_id: int, session_id):
    scan = db.get(Scan, scan_id)
    if not scan or (session_id and scan.session_id not in (None, session_id)):
        raise HTTPException(404, "Scan not found.")
    return scan


@router.get("")
def list_scans(q: str | None = None, crop: str | None = None, status: str | None = Query(default=None, pattern="^(healthy|diseased)$"),
               sort: str = Query(default="date_desc", pattern="^(date_desc|date_asc|conf_desc|conf_asc)$"),
               limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0),
               db: Session = Depends(get_db), session_id: str | None = Depends(get_session_id)):
    qry = db.query(Scan)
    if session_id:
        qry = qry.filter(or_(Scan.session_id == session_id, Scan.session_id.is_(None)))
    if crop:
        qry = qry.filter(Scan.crop == crop)
    if status:
        qry = qry.filter(Scan.is_healthy == (status == "healthy"))
    if q:
        qry = qry.filter(or_(Scan.predicted_class.ilike(f"%{q}%"), Scan.original_name.ilike(f"%{q}%")))
    total = qry.count()
    rows = qry.order_by(SORTS[sort]).offset(offset).limit(limit).all()
    items = [{"scan_id": s.id, "created_at": iso(s.created_at), "predicted_class": s.predicted_class,
              "display_name": display_name(s.predicted_class), "crop": s.crop, "is_healthy": s.is_healthy,
              "confidence": s.confidence, "image_url": file_url("uploads", s.image_file),
              "risk_category": (s.risk or {}).get("category")} for s in rows]
    return {"total": total, "items": items}


@router.get("/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(get_db), session_id: str | None = Depends(get_session_id)):
    return scan_payload(_own(db, scan_id, session_id))


@router.delete("/{scan_id}", status_code=204)
def delete_scan(scan_id: int, db: Session = Depends(get_db), session_id: str | None = Depends(get_session_id)):
    scan = _own(db, scan_id, session_id)
    (settings.uploads_dir / scan.image_file).unlink(missing_ok=True)
    for f in settings.gradcam_dir.glob(f"scan{scan.id}_*"):
        f.unlink(missing_ok=True)
    db.delete(scan)
    db.commit()
