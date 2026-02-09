from fastapi import APIRouter

from app.api.v1.ads import router as ads_router
from app.api.v1.analysis import router as analysis_router

api_router = APIRouter()

api_router.include_router(ads_router, prefix="/ads", tags=["ads"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
