from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import httpx
from database import get_db
from schemas.report import ReportCreate, ReportResponse, ReportList
from models.report import Report
from config import settings
from api.v1.deps import get_current_user
import uuid
from datetime import datetime

router = APIRouter()

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(data: ReportCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    report = Report(id=str(uuid.uuid4()), report_id=f"RPT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}", **data.model_dump(), created_by=current_user["id"], status="generating")
    db.add(report)
    await db.commit()
    await db.refresh(report)
    background_tasks.add_task(generate_report_async, report.id, data.inspection_id)
    return report

async def generate_report_async(report_id: str, inspection_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://localhost:8000/api/v1/inspections/{inspection_id}", timeout=30.0)
            inspection_data = response.json()
            response = await client.get(f"http://localhost:8000/api/v1/detections?inspection_id={inspection_id}&page_size=1000", timeout=30.0)
            detections_data = response.json()
            report_payload = {
                "inspection_id": inspection_id,
                "statistics": {
                    "total_assets": inspection_data.get("total_assets", 0),
                    "total_defects": inspection_data.get("total_defects", 0),
                    "critical": inspection_data.get("critical_count", 0),
                    "high": inspection_data.get("high_count", 0),
                    "medium": inspection_data.get("medium_count", 0),
                    "low": inspection_data.get("low_count", 0)
                },
                "detections": detections_data.get("items", [])
            }
            response = await client.post(f"{settings.AI_ENGINE_URL}/report/generate", json=report_payload, timeout=60.0)
            result = response.json()
        except Exception as e:
            print(f"Report generation failed: {e}")

@router.get("", response_model=ReportList)
async def list_reports(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), inspection_id: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Report)
    if inspection_id:
        query = query.where(Report.inspection_id == inspection_id)
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    query = query.order_by(desc(Report.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return ReportList(items=items, total=total, page=page, page_size=page_size)

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Report).where(Report.report_id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/{report_id}/download")
async def download_report(report_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Report).where(Report.report_id == report_id))
    report = result.scalar_one_or_none()
    if not report or not report.file_path:
        raise HTTPException(status_code=404, detail="Report file not found")
    from fastapi.responses import FileResponse
    return FileResponse(report.file_path, media_type="application/pdf", filename=f"{report.report_id}.pdf")
