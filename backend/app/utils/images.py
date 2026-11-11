import io
import uuid

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

from app.config import settings

ALLOWED = {"JPEG": ".jpg", "PNG": ".png"}


def validate_and_save(data: bytes) -> str:
    """Validate bytes as a real JPEG/PNG, re-encode (strips metadata/payloads) and store under a random name."""
    if not data:
        raise HTTPException(400, "Empty file.")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(413, f"File too large. Maximum is {settings.max_upload_bytes // (1024 * 1024)} MB.")
    try:
        with Image.open(io.BytesIO(data)) as im:
            fmt = im.format
            im.load()
            if fmt not in ALLOWED:
                raise HTTPException(415, "Only JPEG and PNG images are supported.")
            if min(im.size) < 64:
                raise HTTPException(400, "Image is too small (minimum 64 px on the shorter side).")
            if max(im.size) > 8000:
                raise HTTPException(400, "Image is too large (maximum 8000 px).")
            rgb = im.convert("RGB")
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(400, "The file is not a valid image.")
    name = f"{uuid.uuid4().hex}.jpg"
    rgb.save(settings.uploads_dir / name, quality=95)
    return name
