import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routes import analytics, explain, health, predict, reports, scans, tools, weather
from app.services.prediction_service import ModelNotReady, prediction_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("agrimind")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app import models  # noqa: F401  (registers tables with Base)
    Base.metadata.create_all(bind=engine)
    try:
        prediction_service.load()
    except ModelNotReady as e:
        log.warning("Model not loaded at startup: %s", e)
    yield


app = FastAPI(title="AgriMind Fusion API", version="0.1.0", lifespan=lifespan,
              description="Crop disease detection (MobileNetV2) + Grad-CAM + rule-based environmental context.")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
app.mount("/files/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")
app.mount("/files/gradcam", StaticFiles(directory=settings.gradcam_dir), name="gradcam")

for r in (health.router, predict.router, explain.router, scans.router, weather.router, tools.router,
          analytics.router, reports.router):
    app.include_router(r)


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    log.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Check the backend logs."})
