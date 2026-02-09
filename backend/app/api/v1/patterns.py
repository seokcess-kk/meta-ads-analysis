"""Pattern analysis API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.pattern_analyzer import (
    analyze_patterns,
    generate_formula,
    get_insights,
    get_patterns,
)

router = APIRouter()


class PatternResponse(BaseModel):
    """Response model for a single pattern."""
    id: int
    analysis_type: str
    field_name: str
    field_value: str
    successful_count: int
    successful_ratio: float
    general_count: int
    general_ratio: float
    lift: float
    is_pattern: bool


class AnalyzeResponse(BaseModel):
    """Response model for pattern analysis."""
    total_ads: int = 0
    successful_ads: int = 0
    general_ads: int = 0
    patterns_found: int
    all_patterns_analyzed: int = 0
    message: Optional[str] = None


class InsightItem(BaseModel):
    """Individual insight item."""
    title: str
    description: str


class FormulaResponse(BaseModel):
    """Response model for success formula."""
    formula: str = ""
    insights: List[InsightItem] = []
    strategies: List[InsightItem] = []
    confidence: float = 0.0
    error: Optional[str] = None


class InsightResponse(BaseModel):
    """Response model for an insight."""
    id: int
    type: str
    title: str
    description: str
    confidence: float
    generated_at: Optional[str]


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    db: AsyncSession = Depends(get_db),
    industry: Optional[str] = Query(None, description="Filter by industry"),
):
    """
    Analyze patterns comparing successful vs general ads.

    This endpoint:
    1. Separates ads into successful (top 20%) and general groups
    2. Analyzes distribution of image and copy analysis fields
    3. Calculates lift for each field value
    4. Identifies patterns with lift >= 1.5
    """
    result = await analyze_patterns(db, industry)
    return AnalyzeResponse(**result)


@router.get("", response_model=List[PatternResponse])
async def list_patterns(
    db: AsyncSession = Depends(get_db),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    patterns_only: bool = Query(True, description="Only return significant patterns"),
):
    """
    Get analyzed patterns.

    Returns patterns with lift values and statistics.
    """
    patterns = await get_patterns(db, industry, patterns_only)
    return [PatternResponse(**p) for p in patterns]


@router.post("/formula", response_model=FormulaResponse)
async def create_formula(
    db: AsyncSession = Depends(get_db),
    industry: Optional[str] = Query(None, description="Filter by industry"),
):
    """
    Generate success formula using Claude AI.

    Based on identified patterns, generates:
    - A success formula (one sentence)
    - Key insights (3-5 items)
    - Recommended strategies
    """
    result = await generate_formula(db, industry)
    return FormulaResponse(**result)


@router.get("/formula", response_model=FormulaResponse)
async def get_formula(
    db: AsyncSession = Depends(get_db),
    industry: Optional[str] = Query(None, description="Filter by industry"),
):
    """
    Get the generated success formula.

    Returns the latest formula and insights.
    """
    insights = await get_insights(db, industry)

    formula = ""
    insight_list = []
    strategy_list = []
    confidence = 0.0

    for insight in insights:
        if insight["type"] == "formula":
            formula = insight["description"]
            confidence = insight["confidence"]
        elif insight["type"] == "insight":
            insight_list.append(InsightItem(
                title=insight["title"],
                description=insight["description"]
            ))
        elif insight["type"] == "strategy":
            strategy_list.append(InsightItem(
                title=insight["title"],
                description=insight["description"]
            ))

    return FormulaResponse(
        formula=formula,
        insights=insight_list,
        strategies=strategy_list,
        confidence=confidence,
    )


@router.get("/insights", response_model=List[InsightResponse])
async def list_insights(
    db: AsyncSession = Depends(get_db),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    type: Optional[str] = Query(None, description="Filter by insight type"),
):
    """
    Get all generated insights.

    Types: formula, insight, strategy
    """
    insights = await get_insights(db, industry, type)
    return [InsightResponse(**i) for i in insights]
