from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    width: float
    height: float
    center_x: float
    center_y: float

class GPS(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None

class DetectionBase(BaseModel):
    class_name: str
    confidence: float = Field(..., ge=0, le=1)
    severity: str
    bbox: BBox
    gps: Optional[GPS] = None

class DetectionCreate(DetectionBase):
    inspection_id: str
    asset_id: Optional[str] = None
    class_id: Optional[int] = None
    original_image_path: Optional[str] = None
    annotated_image_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DetectionUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    severity: Optional[str] = None

class DetectionResponse(DetectionBase):
    id: str
    inspection_id: str
    asset_id: Optional[str] = None
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class DetectionList(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
