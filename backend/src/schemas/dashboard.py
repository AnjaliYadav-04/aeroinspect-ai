from typing import Dict, List, Any
from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_inspections: int
    total_assets: int
    total_defects: int
    critical_issues: int
    high_issues: int
    inspections_this_month: int
    avg_defects_per_inspection: float
    health_score_avg: float

class SeverityDistribution(BaseModel):
    critical: int
    high: int
    medium: int
    low: int

class RecentInspection(BaseModel):
    id: str
    title: str
    site_name: str
    status: str
    defect_count: int
    created_at: str

class AssetHealth(BaseModel):
    healthy: int
    degraded: int
    critical: int
    offline: int

class DashboardResponse(BaseModel):
    stats: DashboardStats
    severity_distribution: SeverityDistribution
    recent_inspections: List[RecentInspection]
    asset_health: AssetHealth
    monthly_trend: List[Dict[str, Any]]
    top_defect_types: List[Dict[str, Any]]
