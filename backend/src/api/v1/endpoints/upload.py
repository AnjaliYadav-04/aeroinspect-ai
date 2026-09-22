import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from config import settings
from api.v1.deps import get_current_user

router = APIRouter()

@router.post("/image")
async def upload_image(file: UploadFile = File(...), inspection_id: str = None, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "tiff", "tif"]:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, inspection_id or "general")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": filename, "original_name": file.filename, "path": file_path, "size": len(content), "content_type": file.content_type, "inspection_id": inspection_id}

@router.post("/video")
async def upload_video(file: UploadFile = File(...), inspection_id: str = None, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["mp4", "avi", "mov", "mkv"]:
        raise HTTPException(status_code=400, detail="Unsupported video format")
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, inspection_id or "general")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": filename, "original_name": file.filename, "path": file_path, "size": len(content), "content_type": file.content_type, "inspection_id": inspection_id}
