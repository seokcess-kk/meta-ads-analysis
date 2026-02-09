"""Pattern analysis service for identifying successful ad patterns."""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.claude import claude_client
from app.models.ad import (
    AdRaw,
    AdsAnalysisCopy,
    AdsAnalysisImage,
    AdSuccessScore,
    PatternAnalysis,
    PatternInsight,
)

logger = logging.getLogger(__name__)

# Fields to analyze for patterns
IMAGE_FIELDS = [
    ("color_tone", "색조"),
    ("has_person", "인물 포함"),
    ("layout_type", "레이아웃"),
    ("saturation", "채도"),
    ("atmosphere", "분위기"),
]

COPY_FIELDS = [
    ("formality", "격식"),
    ("emotion", "감정"),
    ("style", "스타일"),
    ("core_message", "핵심 메시지"),
]

# Lift threshold for identifying patterns
LIFT_THRESHOLD = 1.5


async def analyze_patterns(
    db: AsyncSession,
    industry: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze patterns comparing successful vs general ads.

    Returns pattern analysis statistics.
    """
    # Get ads with analysis and success scores
    query = (
        select(AdRaw)
        .options(
            selectinload(AdRaw.image_analysis),
            selectinload(AdRaw.copy_analysis),
            selectinload(AdRaw.success_score),
        )
        .join(AdSuccessScore)
    )

    if industry:
        query = query.where(AdRaw.industry == industry)

    result = await db.execute(query)
    ads = result.scalars().all()

    if not ads:
        return {"patterns_found": 0, "insights_generated": 0}

    # Separate successful and general ads
    successful_ads = [ad for ad in ads if ad.success_score and ad.success_score.is_successful]
    general_ads = [ad for ad in ads if ad.success_score and not ad.success_score.is_successful]

    if not successful_ads or not general_ads:
        return {"patterns_found": 0, "insights_generated": 0, "message": "Not enough data"}

    # Clear existing patterns for this industry
    delete_query = delete(PatternAnalysis)
    if industry:
        delete_query = delete_query.where(PatternAnalysis.industry == industry)
    else:
        delete_query = delete_query.where(PatternAnalysis.industry.is_(None))
    await db.execute(delete_query)

    # Analyze image patterns
    image_patterns = _analyze_field_patterns(
        successful_ads,
        general_ads,
        "image",
        IMAGE_FIELDS,
        lambda ad: ad.image_analysis,
    )

    # Analyze copy patterns
    copy_patterns = _analyze_field_patterns(
        successful_ads,
        general_ads,
        "copy",
        COPY_FIELDS,
        lambda ad: ad.copy_analysis,
    )

    all_patterns = image_patterns + copy_patterns

    # Save patterns to database
    patterns_found = 0
    for pattern in all_patterns:
        pa = PatternAnalysis(
            analysis_type=pattern["analysis_type"],
            field_name=pattern["field_name"],
            field_value=str(pattern["field_value"]),
            successful_count=pattern["successful_count"],
            successful_ratio=pattern["successful_ratio"],
            general_count=pattern["general_count"],
            general_ratio=pattern["general_ratio"],
            lift=pattern["lift"],
            is_pattern=pattern["is_pattern"],
            industry=industry,
        )
        db.add(pa)
        if pattern["is_pattern"]:
            patterns_found += 1

    await db.commit()

    return {
        "total_ads": len(ads),
        "successful_ads": len(successful_ads),
        "general_ads": len(general_ads),
        "patterns_found": patterns_found,
        "all_patterns_analyzed": len(all_patterns),
    }


def _analyze_field_patterns(
    successful_ads: List[AdRaw],
    general_ads: List[AdRaw],
    analysis_type: str,
    fields: List[tuple],
    get_analysis,
) -> List[Dict]:
    """Analyze patterns for a set of fields."""
    patterns = []

    for field_name, field_label in fields:
        # Count values in successful ads
        successful_counts = defaultdict(int)
        successful_total = 0
        for ad in successful_ads:
            analysis = get_analysis(ad)
            if analysis:
                value = getattr(analysis, field_name, None)
                if value is not None:
                    successful_counts[str(value)] += 1
                    successful_total += 1

        # Count values in general ads
        general_counts = defaultdict(int)
        general_total = 0
        for ad in general_ads:
            analysis = get_analysis(ad)
            if analysis:
                value = getattr(analysis, field_name, None)
                if value is not None:
                    general_counts[str(value)] += 1
                    general_total += 1

        # Skip if not enough data
        if successful_total < 5 or general_total < 5:
            continue

        # Calculate patterns for each value
        all_values = set(successful_counts.keys()) | set(general_counts.keys())
        for value in all_values:
            successful_count = successful_counts.get(value, 0)
            general_count = general_counts.get(value, 0)

            successful_ratio = successful_count / successful_total if successful_total > 0 else 0
            general_ratio = general_count / general_total if general_total > 0 else 0

            # Calculate lift
            lift = successful_ratio / general_ratio if general_ratio > 0 else (
                float('inf') if successful_ratio > 0 else 0
            )

            patterns.append({
                "analysis_type": analysis_type,
                "field_name": field_name,
                "field_value": value,
                "successful_count": successful_count,
                "successful_ratio": round(successful_ratio, 4),
                "general_count": general_count,
                "general_ratio": round(general_ratio, 4),
                "lift": round(lift, 2) if lift != float('inf') else 99.99,
                "is_pattern": lift >= LIFT_THRESHOLD,
            })

    return patterns


async def get_patterns(
    db: AsyncSession,
    industry: Optional[str] = None,
    patterns_only: bool = True
) -> List[Dict]:
    """Get analyzed patterns."""
    query = select(PatternAnalysis)

    if industry:
        query = query.where(PatternAnalysis.industry == industry)
    else:
        query = query.where(PatternAnalysis.industry.is_(None))

    if patterns_only:
        query = query.where(PatternAnalysis.is_pattern == True)

    query = query.order_by(PatternAnalysis.lift.desc())

    result = await db.execute(query)
    patterns = result.scalars().all()

    return [
        {
            "id": p.id,
            "analysis_type": p.analysis_type,
            "field_name": p.field_name,
            "field_value": p.field_value,
            "successful_count": p.successful_count,
            "successful_ratio": p.successful_ratio,
            "general_count": p.general_count,
            "general_ratio": p.general_ratio,
            "lift": p.lift,
            "is_pattern": p.is_pattern,
        }
        for p in patterns
    ]


async def generate_formula(
    db: AsyncSession,
    industry: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate success formula using Claude based on identified patterns.

    Returns generated insight.
    """
    # Get top patterns
    patterns = await get_patterns(db, industry, patterns_only=True)

    if not patterns:
        return {"error": "No patterns found. Run pattern analysis first."}

    # Build prompt for Claude
    pattern_summary = []
    for p in patterns[:10]:  # Top 10 patterns
        pattern_summary.append(
            f"- {p['field_name']}={p['field_value']}: "
            f"성공 광고 {p['successful_ratio']*100:.1f}% vs 일반 광고 {p['general_ratio']*100:.1f}% "
            f"(Lift: {p['lift']:.2f}x)"
        )

    prompt = f"""# 광고 성공 패턴 분석 결과를 기반으로 성공 공식 생성

## 발견된 주요 패턴
{chr(10).join(pattern_summary)}

## 요청
위 패턴을 분석하여 다음을 생성해주세요:

1. **성공 공식 (한 문장)**: 데이터 기반의 성공적인 광고 제작 공식
2. **핵심 인사이트 (3-5개)**: 각 패턴에서 도출한 실행 가능한 인사이트
3. **추천 전략**: 새 광고 제작 시 적용할 구체적 전략

응답은 반드시 다음 JSON 형식으로만 응답해주세요:

```json
{{
  "formula": "성공 공식 한 문장",
  "insights": [
    {{"title": "인사이트 제목", "description": "구체적 설명"}},
    ...
  ],
  "strategies": [
    {{"title": "전략 제목", "description": "구체적 실행 방안"}},
    ...
  ],
  "confidence": 0.85
}}
```"""

    try:
        # Call Claude
        message = claude_client.client.messages.create(
            model=claude_client.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
        result = claude_client._parse_json_response(response_text)

        if not result:
            return {"error": "Failed to parse Claude response"}

        # Clear existing insights
        delete_query = delete(PatternInsight)
        if industry:
            delete_query = delete_query.where(PatternInsight.industry == industry)
        else:
            delete_query = delete_query.where(PatternInsight.industry.is_(None))
        await db.execute(delete_query)

        # Save formula insight
        formula_insight = PatternInsight(
            insight_type="formula",
            title="성공 광고 공식",
            description=result.get("formula", ""),
            supporting_patterns={"patterns": [p["field_name"] for p in patterns[:10]]},
            confidence=result.get("confidence", 0.8),
            industry=industry,
        )
        db.add(formula_insight)

        # Save individual insights
        for insight in result.get("insights", []):
            pi = PatternInsight(
                insight_type="insight",
                title=insight.get("title", ""),
                description=insight.get("description", ""),
                confidence=result.get("confidence", 0.8),
                industry=industry,
            )
            db.add(pi)

        # Save strategies
        for strategy in result.get("strategies", []):
            pi = PatternInsight(
                insight_type="strategy",
                title=strategy.get("title", ""),
                description=strategy.get("description", ""),
                confidence=result.get("confidence", 0.8),
                industry=industry,
            )
            db.add(pi)

        await db.commit()

        return {
            "formula": result.get("formula", ""),
            "insights": result.get("insights", []),
            "strategies": result.get("strategies", []),
            "confidence": result.get("confidence", 0.8),
        }

    except Exception as e:
        logger.error(f"Error generating formula: {e}")
        return {"error": str(e)}


async def get_insights(
    db: AsyncSession,
    industry: Optional[str] = None,
    insight_type: Optional[str] = None
) -> List[Dict]:
    """Get generated insights."""
    query = select(PatternInsight)

    if industry:
        query = query.where(PatternInsight.industry == industry)
    else:
        query = query.where(PatternInsight.industry.is_(None))

    if insight_type:
        query = query.where(PatternInsight.insight_type == insight_type)

    query = query.order_by(PatternInsight.generated_at.desc())

    result = await db.execute(query)
    insights = result.scalars().all()

    return [
        {
            "id": i.id,
            "type": i.insight_type,
            "title": i.title,
            "description": i.description,
            "confidence": i.confidence,
            "generated_at": i.generated_at.isoformat() if i.generated_at else None,
        }
        for i in insights
    ]
