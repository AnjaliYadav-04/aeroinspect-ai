from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: str = Field(..., pattern="^(solar_panel|turbine|pylon|transformer|inverter|road|bridge|pipeline|tank|building)$")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    manufacturer: Optional[str] = None
    capacity_kw: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class AssetCreate(AssetBase):
    inspection_id: Optional[str] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    health_score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    next_maintenance_date: Optional[datetime] = None

class AssetResponse(AssetBase):
    id: str
    asset_id: str
    health_score: float
    status: str
    last_inspection_date: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

class AssetList(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
