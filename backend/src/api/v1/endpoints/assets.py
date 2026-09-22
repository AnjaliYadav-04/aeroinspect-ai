from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetList
from models.asset import Asset
from api.v1.deps import get_current_user
import uuid
from datetime import datetime

router = APIRouter()

@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(data: AssetCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    asset = Asset(id=str(uuid.uuid4()), asset_id=f"AST-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}", **data.model_dump())
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset

@router.get("", response_model=AssetList)
async def list_assets(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), asset_type: Optional[str] = None, status: Optional[str] = None, inspection_id: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Asset)
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    if status:
        query = query.where(Asset.status == status)
    if inspection_id:
        query = query.where(Asset.inspection_id == inspection_id)
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    query = query.order_by(desc(Asset.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return AssetList(items=items, total=total, page=page, page_size=page_size)

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Asset).where(Asset.asset_id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(asset_id: str, data: AssetUpdate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Asset).where(Asset.asset_id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(asset, field, value)
    await db.commit()
    await db.refresh(asset)
    return asset
