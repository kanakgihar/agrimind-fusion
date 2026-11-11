"""Central configuration. Everything comes from environment variables with safe local defaults."""
import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / "backend" / ".env")


def _dir(env_name: str, default: Path) -> Path:
    v = os.getenv(env_name, "").strip()
    return Path(v) if v else default


class Settings:
    models_dir: Path = _dir("MODELS_DIR", REPO_ROOT / "models")
    storage_dir: Path = _dir("STORAGE_DIR", REPO_ROOT / "storage")
    model_file: str = os.getenv("MODEL_FILE", "mobilenetv2_final.keras")
    cors_origins: list = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    max_upload_bytes: int = int(float(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024)
    low_conf: float = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.60"))
    ee_project: str = os.getenv("EE_PROJECT", "")
    ee_service_account: str = os.getenv("EE_SERVICE_ACCOUNT", "")
    ee_key_file: str = os.getenv("EE_PRIVATE_KEY_FILE", "")

    @property
    def database_url(self) -> str:
        url = os.getenv("DATABASE_URL", "").strip()
        if not url:
            return f"sqlite:///{(self.storage_dir / 'agrimind.db').as_posix()}"
        if url.startswith("postgres://"):  # Render style URL
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    @property
    def uploads_dir(self) -> Path:
        return self.storage_dir / "uploads"

    @property
    def gradcam_dir(self) -> Path:
        return self.storage_dir / "gradcam"


settings = Settings()
for d in (settings.storage_dir, settings.uploads_dir, settings.gradcam_dir):
    d.mkdir(parents=True, exist_ok=True)
