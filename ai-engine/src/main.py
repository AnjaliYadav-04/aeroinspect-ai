import os
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import aiofiles
from config import settings
from services.detection_service import detection_service
from services.report_generator import report_generator

app = FastAPI(title="AI Drone Inspection Engine", description="YOLO-based detection and analysis service", version="2.0.0")

class BatchRequest(BaseModel):
    inspection_id: str
    image_paths: List[str]

class ReportRequest(BaseModel):
    inspection_id: str
    statistics: dict
    detections: List[dict]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": settings.MODEL_PATH, "device": settings.DEVICE, "timestamp": datetime.utcnow().isoformat()}

@app.post("/detect/image")
async def detect_image(inspection_id: str, asset_id: Optional[str] = None, file: UploadFile = File(...)):
    upload_path = f"/tmp/{file.filename}"
    async with aiofiles.open(upload_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    result = await detection_service.process_image(upload_path, inspection_id, asset_id)
    os.remove(upload_path)
    return JSONResponse(content=result)

@app.post("/detect/batch")
async def detect_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    result = await detection_service.process_batch(request.image_paths, request.inspection_id)
    background_tasks.add_task(detection_service.notify_backend, result)
    return result

@app.post("/detect/video")
async def detect_video(inspection_id: str, sample_interval: int = 30, file: UploadFile = File(...)):
    upload_path = f"/tmp/{file.filename}"
    async with aiofiles.open(upload_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    result = await detection_service.process_video(upload_path, inspection_id, sample_interval)
    os.remove(upload_path)
    return result

@app.post("/report/generate")
async def generate_report(request: ReportRequest):
    try:
        report_path = report_generator.generate_inspection_report({"inspection_id": request.inspection_id, "statistics": request.statistics, "detections": request.detections})
        return {"status": "success", "report_path": report_path, "download_url": f"/report/download/{os.path.basename(report_path)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report/download/{filename}")
async def download_report(filename: str):
    file_path = os.path.join("/app/reports", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

@app.get("/classes")
async def get_detection_classes():
    return {"classes": settings.DETECTION_CLASSES, "severity_mapping": settings.SEVERITY_WEIGHTS}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
