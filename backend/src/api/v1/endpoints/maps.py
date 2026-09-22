from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models.detection import Detection
from models.asset import Asset
from api.v1.deps import get_current_user

router = APIRouter()

@router.get("/detections")
async def get_detection_geojson(inspection_id: Optional[str] = None, severity: Optional[str] = None, bbox: Optional[str] = Query(None, description="minLon,minLat,maxLon,maxLat"), db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Detection.id, Detection.class_name, Detection.severity, Detection.confidence, Detection.latitude, Detection.longitude, Detection.status).where(Detection.latitude.isnot(None), Detection.longitude.isnot(None))
    if severity:
        query = query.where(Detection.severity == severity)
    if bbox:
        min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(","))
        query = query.where(Detection.longitude >= min_lon, Detection.longitude <= max_lon, Detection.latitude >= min_lat, Detection.latitude <= max_lat)
    result = await db.execute(query)
    rows = result.all()
    features = []
    for row in rows:
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [row.longitude, row.latitude]}, "properties": {"id": str(row.id), "class_name": row.class_name, "severity": row.severity, "confidence": row.confidence, "status": row.status}})
    return {"type": "FeatureCollection", "features": features}

@router.get("/assets")
async def get_asset_geojson(status: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Asset.id, Asset.asset_id, Asset.name, Asset.asset_type, Asset.latitude, Asset.longitude, Asset.health_score, Asset.status).where(Asset.latitude.isnot(None), Asset.longitude.isnot(None))
    if status:
        query = query.where(Asset.status == status)
    result = await db.execute(query)
    rows = result.all()
    features = []
    for row in rows:
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [row.longitude, row.latitude]}, "properties": {"id": str(row.id), "asset_id": row.asset_id, "name": row.name, "type": row.asset_type, "health_score": row.health_score, "status": row.status}})
    return {"type": "FeatureCollection", "features": features}

@router.get("/clusters")
async def get_defect_clusters(inspection_id: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Detection.latitude, Detection.longitude, Detection.severity).where(Detection.latitude.isnot(None), Detection.longitude.isnot(None))
    result = await db.execute(query)
    rows = result.all()
    clusters = []
    for row in rows:
        weight = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}.get(row.severity, 0.1)
        clusters.append({"lat": row.latitude, "lon": row.longitude, "weight": weight})
    return {"clusters": clusters}
