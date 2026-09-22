import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/app/models/yolov8n-drone.pt")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
    IOU_THRESHOLD: float = 0.45
    DEVICE: str = os.getenv("DEVICE", "cpu")
    DETECTION_CLASSES: dict = {
        0: "crack", 1: "hotspot", 2: "soiling", 3: "delamination",
        4: "broken_panel", 5: "vegetation_overgrowth", 6: "structural_damage",
        7: "corrosion", 8: "missing_component", 9: "water_damage",
        10: "worker", 11: "vehicle", 12: "safety_violation"
    }
    SEVERITY_WEIGHTS: dict = {
        "crack": "high", "hotspot": "critical", "soiling": "low",
        "delamination": "medium", "broken_panel": "critical",
        "vegetation_overgrowth": "low", "structural_damage": "high",
        "corrosion": "medium", "missing_component": "medium",
        "water_damage": "high", "worker": "info", "vehicle": "info",
        "safety_violation": "critical"
    }
    UPLOAD_DIR: str = "/app/uploads"
    PROCESSED_DIR: str = "/app/processed"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://backend:8000")
    class Config:
        env_file = ".env"

settings = Settings()
