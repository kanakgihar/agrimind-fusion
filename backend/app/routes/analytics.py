import csv
import io
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scan import Scan
from app.services.disease_knowledge import KNOWLEDGE, display_name
from app.utils.deps import get_session_id
from app.utils.payload import iso

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _query(db, session_id, date_from, date_to, crop):
    q = db.query(Scan)
    if session_id:
        q = q.filter(or_(Scan.session_id == session_id, Scan.session_id.is_(None)))
    if crop:
        q = q.filter(Scan.crop == crop)
    if date_from:
        q = q.filter(Scan.created_at >= datetime.fromisoformat(date_from).replace(tzinfo=timezone.utc))
    if date_to:
        q = q.filter(Scan.created_at < datetime.fromisoformat(date_to).replace(tzinfo=timezone.utc) + timedelta(days=1))
    return q.order_by(Scan.created_at.desc()).all()


@router.get("/summary")
def summary(date_from: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
            date_to: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
            crop: str | None = None, db: Session = Depends(get_db), session_id: str | None = Depends(get_session_id)):
    scans = _query(db, session_id, date_from, date_to, crop)
    total = len(scans)
    healthy = sum(1 for s in scans if s.is_healthy)
    by_class = Counter(display_name(s.predicted_class) for s in scans if not s.is_healthy)
    by_crop = defaultdict(lambda: {"healthy": 0, "diseased": 0})
    per_day = Counter()
    risk_dist = Counter()
    env_trend = []
    alerts = []
    for s in scans:
        by_crop[s.crop]["healthy" if s.is_healthy else "diseased"] += 1
        per_day[s.created_at.date().isoformat()] += 1
        if s.risk:
            risk_dist[s.risk["category"]] += 1
            env_trend.append({"date": iso(s.created_at), "temperature_c": s.risk["inputs"].get("temperature_c"),
                              "humidity_pct": s.risk["inputs"].get("humidity_pct"), "score": s.risk["score"]})
    for s in scans[:20]:
        k = KNOWLEDGE.get(s.predicted_class, {})
        if not s.is_healthy and (k.get("urgency") == "high" or (s.risk or {}).get("category") == "High"):
            alerts.append({"scan_id": s.id, "message": f"{display_name(s.predicted_class)}: high urgency or high environmental risk. Review the recommendations."})
    return {
        "total": total, "healthy": healthy, "diseased": total - healthy,
        "avg_confidence": round(sum(s.confidence for s in scans) / total, 4) if total else None,
        "disease_distribution": [{"name": k, "count": v} for k, v in by_class.most_common()],
        "crop_stats": [{"crop": c, **v} for c, v in sorted(by_crop.items())],
        "scans_per_day": [{"date": d, "count": n} for d, n in sorted(per_day.items())],
        "risk_distribution": [{"category": c, "count": risk_dist.get(c, 0)} for c in ("Low", "Moderate", "High")],
        "environment_trend": list(reversed(env_trend)),
        "satellite_trend": {"available": False, "note": "Satellite results are not stored yet."},
        "recent": [{"scan_id": s.id, "display_name": display_name(s.predicted_class), "confidence": s.confidence,
                    "is_healthy": s.is_healthy, "created_at": iso(s.created_at), "image_url": f"/files/uploads/{s.image_file}"}
                   for s in scans[:6]],
        "alerts": alerts[:5],
    }


@router.get("/export")
def export(date_from: str | None = None, date_to: str | None = None, crop: str | None = None,
           db: Session = Depends(get_db), session_id: str | None = Depends(get_session_id)):
    rows = _query(db, session_id, date_from, date_to, crop)
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["scan_id", "created_at", "crop", "predicted_class", "is_healthy", "confidence", "temperature_c",
                "humidity_pct", "rainfall_mm", "soil_moisture", "risk_category", "risk_score"])
    for s in rows:
        i = (s.risk or {}).get("inputs", {})
        w.writerow([s.id, iso(s.created_at), s.crop, s.predicted_class, s.is_healthy, round(s.confidence, 4),
                    i.get("temperature_c"), i.get("humidity_pct"), i.get("rainfall_mm"), i.get("soil_moisture"),
                    (s.risk or {}).get("category"), (s.risk or {}).get("score")])
    return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=agrimind_scans.csv"})
