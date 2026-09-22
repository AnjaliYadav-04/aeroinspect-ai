from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from schemas.detection import DetectionCreate, DetectionUpdate, DetectionResponse, DetectionList
from models.detection import Detection
from api.v1.deps import get_current_user

router = APIRouter()

@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_detections_batch(data: dict, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    detections_data = data.get("detections", [])
    inspection_id = data.get("inspection_id")
    created = []
    for det in detections_data:
        detection = Detection(
            id=str(__import__('uuid').uuid4()),
            class_name=det.get("class_name", "unknown"),
            class_id=det.get("class_id"),
            confidence=det.get("confidence", 0),
            severity=det.get("severity", "low"),
            bbox_x1=det.get("bbox", {}).get("x1"),
            bbox_y1=det.get("bbox", {}).get("y1"),
            bbox_x2=det.get("bbox", {}).get("x2"),
            bbox_y2=det.get("bbox", {}).get("y2"),
            bbox_width=det.get("bbox", {}).get("width"),
            bbox_height=det.get("bbox", {}).get("height"),
            center_x=det.get("bbox", {}).get("center_x"),
            center_y=det.get("bbox", {}).get("center_y"),
            latitude=det.get("gps", {}).get("latitude") if det.get("gps") else None,
            longitude=det.get("gps", {}).get("longitude") if det.get("gps") else None,
            altitude=det.get("gps", {}).get("altitude") if det.get("gps") else None,
            original_image_path=det.get("original_image_path"),
            annotated_image_path=det.get("annotated_image_path"),
            detection_metadata=det.get("metadata"),
            inspection_id=inspection_id
        )
        db.add(detection)
        created.append(detection)
    await db.commit()
    return {"created": len(created), "inspection_id": inspection_id}

@router.get("", response_model=DetectionList)
async def list_detections(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), severity: Optional[str] = None, class_name: Optional[str] = None, status: Optional[str] = None, inspection_id: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Detection)
    if severity:
        query = query.where(Detection.severity == severity)
    if class_name:
        query = query.where(Detection.class_name == class_name)
    if status:
        query = query.where(Detection.status == status)
    if inspection_id:
        query = query.where(Detection.inspection_id == inspection_id)
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    query = query.order_by(desc(Detection.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return DetectionList(items=items, total=total, page=page, page_size=page_size)

@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_detection(detection_id: str, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Detection).where(Detection.id == detection_id))
    detection = result.scalar_one_or_none()
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection

@router.patch("/{detection_id}", response_model=DetectionResponse)
async def update_detection(detection_id: str, data: DetectionUpdate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Detection).where(Detection.id == detection_id))
    detection = result.scalar_one_or_none()
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(detection, field, value)
    await db.commit()
    await db.refresh(detection)
    return detection
