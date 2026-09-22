from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.inspection import Inspection
from schemas.inspection import InspectionCreate, InspectionUpdate

class InspectionService:
    @staticmethod
    async def get_by_id(db: AsyncSession, inspection_id: str) -> Optional[Inspection]:
        result = await db.execute(select(Inspection).where(Inspection.inspection_id == inspection_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_stats(db: AsyncSession, inspection_id: str) -> None:
        from sqlalchemy import func
        from models.detection import Detection
        result = await db.execute(select(func.count(Detection.id), func.sum(func.case((Detection.severity == "critical", 1), else_=0)), func.sum(func.case((Detection.severity == "high", 1), else_=0)), func.sum(func.case((Detection.severity == "medium", 1), else_=0)), func.sum(func.case((Detection.severity == "low", 1), else_=0))).where(Detection.inspection_id == inspection_id))
        row = result.one()
        inspection = await db.get(Inspection, inspection_id)
        if inspection:
            inspection.total_defects = row[0] or 0
            inspection.critical_count = row[1] or 0
            inspection.high_count = row[2] or 0
            inspection.medium_count = row[3] or 0
            inspection.low_count = row[4] or 0
            await db.commit()

inspection_service = InspectionService()
