from fastapi import APIRouter
from api.v1.endpoints import inspections, detections, assets, reports, upload, dashboard, maps,auth

api_router = APIRouter()
api_router.include_router(inspections.router, prefix="/inspections", tags=["inspections"])
api_router.include_router(detections.router, prefix="/detections", tags=["detections"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(maps.router, prefix="/maps", tags=["maps"])

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
