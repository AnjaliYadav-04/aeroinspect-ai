from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from database import get_db
from schemas.inspection import (
    InspectionCreate,
    InspectionUpdate,
    InspectionResponse,
    InspectionList,
    InspectionStats,
)
from models.inspection import Inspection
from api.v1.deps import get_current_user

import uuid
from datetime import datetime


router = APIRouter()


def inspection_to_response(inspection: Inspection) -> InspectionResponse:
    """
    Convert an Inspection SQLAlchemy model into the
    InspectionResponse Pydantic schema.
    """

    return InspectionResponse(
        id=inspection.id,
        inspection_id=inspection.inspection_id,
        title=inspection.title,
        description=inspection.description,
        site_name=inspection.site_name,
        drone_model=inspection.drone_model,
        pilot_name=inspection.pilot_name,
        weather_conditions=inspection.weather_conditions,
        scheduled_at=inspection.scheduled_at,
        status=(
            inspection.status.value
            if hasattr(inspection.status, "value")
            else inspection.status
        ),
        stats=InspectionStats(
            total_assets=inspection.total_assets or 0,
            total_defects=inspection.total_defects or 0,
            critical=inspection.critical_count or 0,
            high=inspection.high_count or 0,
            medium=inspection.medium_count or 0,
            low=inspection.low_count or 0,
        ),
        created_at=inspection.created_at,
        updated_at=inspection.updated_at,
    )


# ============================================================
# CREATE INSPECTION
# ============================================================

@router.post(
    "",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_inspection(
    data: InspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    inspection = Inspection(
        id=str(uuid.uuid4()),
        inspection_id=(
            f"DRN-{datetime.utcnow().strftime('%Y%m%d')}-"
            f"{uuid.uuid4().hex[:6].upper()}"
        ),
        **data.model_dump(),
        created_by=current_user["id"],
    )

    db.add(inspection)

    await db.commit()
    await db.refresh(inspection)

    return inspection_to_response(inspection)


# ============================================================
# LIST INSPECTIONS
# ============================================================

@router.get(
    "",
    response_model=InspectionList,
)
async def list_inspections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    site_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = select(Inspection)

    # Filter by status
    if status:
        query = query.where(
            Inspection.status == status
        )

    # Filter by site name
    if site_name:
        query = query.where(
            Inspection.site_name.ilike(
                f"%{site_name}%"
            )
        )

    # Count total records
    total_result = await db.execute(
        select(func.count()).select_from(
            query.subquery()
        )
    )

    total = total_result.scalar() or 0

    # Pagination
    query = (
        query
        .order_by(desc(Inspection.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)

    items = result.scalars().all()

    return InspectionList(
        items=[
            inspection_to_response(item)
            for item in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


# ============================================================
# GET SINGLE INSPECTION
# ============================================================

@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse,
)
async def get_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(Inspection).where(
            Inspection.inspection_id == inspection_id
        )
    )

    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    return inspection_to_response(inspection)


# ============================================================
# UPDATE INSPECTION
# ============================================================

@router.patch(
    "/{inspection_id}",
    response_model=InspectionResponse,
)
async def update_inspection(
    inspection_id: str,
    data: InspectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(Inspection).where(
            Inspection.inspection_id == inspection_id
        )
    )

    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    # Update only supplied fields
    for field, value in data.model_dump(
        exclude_unset=True
    ).items():

        if value is not None:
            setattr(
                inspection,
                field,
                value,
            )

    await db.commit()
    await db.refresh(inspection)

    return inspection_to_response(inspection)


# ============================================================
# DELETE INSPECTION
# ============================================================

@router.delete(
    "/{inspection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(Inspection).where(
            Inspection.inspection_id == inspection_id
        )
    )

    inspection = result.scalar_one_or_none()

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    await db.delete(inspection)

    await db.commit()

    return None