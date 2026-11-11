from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _now():
    return datetime.now(timezone.utc)


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    image_file: Mapped[str] = mapped_column(String(255))          # file name inside storage/uploads
    original_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    selected_crop: Mapped[str | None] = mapped_column(String(32), nullable=True)
    predicted_class: Mapped[str] = mapped_column(String(100), index=True)
    crop: Mapped[str] = mapped_column(String(32), index=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[float] = mapped_column(Float)
    top3: Mapped[list] = mapped_column(JSON)
    model_version: Mapped[str] = mapped_column(String(64))
    environment: Mapped[dict | None] = mapped_column(JSON, nullable=True)   # user-entered / fetched values
    risk: Mapped[dict | None] = mapped_column(JSON, nullable=True)          # rule-based assessment
    gradcam_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # file names + region stats
