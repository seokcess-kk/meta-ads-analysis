from fastapi import APIRouter

from app.api.v1.ads import router as ads_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.scoring import router as scoring_router
from app.api.v1.patterns import router as patterns_router
from app.api.v1.monitoring import router as monitoring_router

api_router = APIRouter()

api_router.include_router(ads_router, prefix="/ads", tags=["ads"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
api_router.include_router(scoring_router, prefix="/scoring", tags=["scoring"])
api_router.include_router(patterns_router, prefix="/patterns", tags=["patterns"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
