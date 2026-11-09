import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Customs Broker AI Document Extraction & Cross-Check"
    API_V1_STR: str = "/api"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/customs_broker.db")
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    EXPORT_DIR: Path = BASE_DIR / "exports"
    
    # Tolerance settings for cross-check validations
    WEIGHT_TOLERANCE_PERCENT: float = 0.5  # 0.5% tolerance
    WEIGHT_TOLERANCE_KG: float = 5.0       # 5 kg absolute tolerance
    AMOUNT_TOLERANCE_CURRENCY: float = 0.10 # $0.10 rounding tolerance
    
    # Confidence threshold
    CONFIDENCE_THRESHOLD: float = 85.0     # Fields <85% marked as low-confidence
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
