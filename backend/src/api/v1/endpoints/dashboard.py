from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, extract
from datetime import datetime, timedelta
from database import get_db
from schemas.dashboard import DashboardResponse, DashboardStats, SeverityDistribution, AssetHealth, RecentInspection
from models.inspection import Inspection
from models.detection import Detection
from models.asset import Asset
from api.v1.deps import get_current_user

router = APIRouter()

@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    total_inspections_result = await db.execute(select(func.count(Inspection.id)))
    total_inspections = total_inspections_result.scalar()
    total_assets_result = await db.execute(select(func.count(Asset.id)))
    total_assets = total_assets_result.scalar()
    total_defects_result = await db.execute(select(func.count(Detection.id)))
    total_defects = total_defects_result.scalar()
    critical_result = await db.execute(select(func.count(Detection.id)).where(Detection.severity == "critical"))
    critical = critical_result.scalar()
    high_result = await db.execute(select(func.count(Detection.id)).where(Detection.severity == "high"))
    high = high_result.scalar()
    medium_result = await db.execute(select(func.count(Detection.id)).where(Detection.severity == "medium"))
    medium = medium_result.scalar()
    low_result = await db.execute(select(func.count(Detection.id)).where(Detection.severity == "low"))
    low = low_result.scalar()
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_result = await db.execute(select(func.count(Inspection.id)).where(Inspection.created_at >= month_start))
    inspections_this_month = month_result.scalar()
    avg_defects = total_defects / total_inspections if total_inspections > 0 else 0
    health_result = await db.execute(select(func.avg(Asset.health_score)))
    health_avg = health_result.scalar() or 100.0
    healthy_result = await db.execute(select(func.count(Asset.id)).where(Asset.status == "healthy"))
    healthy = healthy_result.scalar()
    degraded_result = await db.execute(select(func.count(Asset.id)).where(Asset.status == "degraded"))
    degraded = degraded_result.scalar()
    critical_assets_result = await db.execute(select(func.count(Asset.id)).where(Asset.status == "critical"))
    critical_assets = critical_assets_result.scalar()
    offline_result = await db.execute(select(func.count(Asset.id)).where(Asset.status == "offline"))
    offline = offline_result.scalar()
    recent_result = await db.execute(select(Inspection).order_by(desc(Inspection.created_at)).limit(5))
    recent_inspections = recent_result.scalars().all()
    monthly_trend = []
    for i in range(5, -1, -1):
        month_date = datetime.utcnow() - timedelta(days=30*i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        count_result = await db.execute(select(func.count(Inspection.id)).where(Inspection.created_at >= month_start, Inspection.created_at < month_end))
        monthly_trend.append({"month": month_date.strftime("%Y-%m"), "inspections": count_result.scalar()})
    defect_types_result = await db.execute(select(Detection.class_name, func.count(Detection.id)).group_by(Detection.class_name).order_by(desc(func.count(Detection.id))).limit(5))
    top_defect_types = [{"type": row[0], "count": row[1]} for row in defect_types_result.all()]
    return DashboardResponse(
        stats=DashboardStats(total_inspections=total_inspections, total_assets=total_assets, total_defects=total_defects, critical_issues=critical, high_issues=high, inspections_this_month=inspections_this_month, avg_defects_per_inspection=round(avg_defects, 2), health_score_avg=round(float(health_avg), 1)),
        severity_distribution=SeverityDistribution(critical=critical, high=high, medium=medium, low=low),
        recent_inspections=[RecentInspection(id=inp.inspection_id, title=inp.title, site_name=inp.site_name or "Unknown", status=inp.status.value, defect_count=inp.total_defects, created_at=inp.created_at.isoformat()) for inp in recent_inspections],
        asset_health=AssetHealth(healthy=healthy, degraded=degraded, critical=critical_assets, offline=offline),
        monthly_trend=monthly_trend,
        top_defect_types=top_defect_types
    )
