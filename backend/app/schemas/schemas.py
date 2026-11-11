from pydantic import BaseModel, Field


class Env(BaseModel):
    temperature_c: float | None = Field(default=None, ge=-30, le=60)
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    rainfall_mm: float | None = Field(default=None, ge=0, le=1000)
    soil_moisture: float | None = Field(default=None, ge=0, le=1)


class SimulatorRequest(BaseModel):
    baseline: Env
    scenario: Env


class RecommendationRequest(BaseModel):
    predicted_class: str
    confidence: float = Field(default=1.0, ge=0, le=1)
    selected_crop: str | None = None
    environment: Env | None = None


class ChatMessage(BaseModel):
    role: str
    content: str = Field(max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    scan_id: int | None = None
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class SatelliteRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    start_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    radius_m: int = Field(default=200, ge=30, le=2000)
    max_cloud_pct: int = Field(default=60, ge=0, le=100)
