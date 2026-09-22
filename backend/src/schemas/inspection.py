from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class InspectionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    site_name: Optional[str] = None
    drone_model: Optional[str] = None
    pilot_name: Optional[str] = None
    weather_conditions: Optional[str] = None
    scheduled_at: Optional[datetime] = None

class InspectionCreate(InspectionBase):
    pass

class InspectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    site_name: Optional[str] = None

class InspectionStats(BaseModel):
    total_assets: int = 0
    total_defects: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

class InspectionResponse(InspectionBase):
    id: str
    inspection_id: str
    status: str
    stats: InspectionStats
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class InspectionList(BaseModel):
    items: List[InspectionResponse]
    total: int
    page: int
    page_size: int
