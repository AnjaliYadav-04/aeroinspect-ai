from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ReportBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    report_type: str = "inspection"

class ReportCreate(ReportBase):
    inspection_id: str

class ReportResponse(ReportBase):
    id: str
    report_id: str
    status: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    summary: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    generated_at: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ReportList(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
