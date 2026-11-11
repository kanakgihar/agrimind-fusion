from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.scan import Scan
from app.services import report_service
from app.utils.deps import get_session_id
from app.utils.payload import scan_payload

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{scan_id}")
async def report(scan_id: int, db: Session = Depends(get_db), session_id: str | None = Depends(get_session_id)):
    scan = db.get(Scan, scan_id)
    if not scan or (session_id and scan.session_id not in (None, session_id)):
        raise HTTPException(404, "Scan not found.")
    p = scan_payload(scan)
    gi = scan.gradcam_info or {}
    overlay = settings.gradcam_dir / gi["overlay"] if gi.get("overlay") else None
    pdf = await run_in_threadpool(report_service.build_pdf, p, p["recommendation"], settings.uploads_dir / scan.image_file, overlay)
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=agrimind_scan_{scan.id}.pdf"})
