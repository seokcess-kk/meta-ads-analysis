"""Scoring API endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.scoring import calculate_all_scores, get_scoring_stats

router = APIRouter()


class ScoreCalculationResponse(BaseModel):
    """Response model for score calculation."""
    calculated: int
    successful: int
    max_impressions_mid: float


class ScoringStatsResponse(BaseModel):
    """Response model for scoring statistics."""
    total_scored: int
    successful_count: int
    success_rate: float
    avg_total_score: float
    avg_duration_score: float
    avg_impressions_score: float
    max_score: float
    min_score: float


@router.post("/calculate", response_model=ScoreCalculationResponse)
async def calculate_scores(db: AsyncSession = Depends(get_db)):
    """
    Calculate success scores for all ads.

    This endpoint calculates and stores success scores based on:
    - Duration score (40% weight): Based on how long the ad has been running
    - Impressions score (60% weight): Based on estimated reach (log normalized)

    Ads in the top 20% (80th percentile) are marked as successful.
    """
    result = await calculate_all_scores(db)
    return ScoreCalculationResponse(**result)


@router.get("/stats", response_model=ScoringStatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Get scoring statistics.

    Returns aggregate statistics about calculated success scores.
    """
    stats = await get_scoring_stats(db)
    return ScoringStatsResponse(**stats)
