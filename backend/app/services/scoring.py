"""Success scoring service for ads."""

import math
from datetime import date, datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ad import AdRaw, AdSuccessScore


def calculate_duration_score(duration_days: int) -> float:
    """
    Calculate duration score (0-100).

    0-7 days: 0-20 points
    8-14 days: 21-40 points
    15-30 days: 41-60 points
    31-60 days: 61-80 points
    60+ days: 81-100 points
    """
    if duration_days <= 7:
        return (duration_days / 7) * 20
    elif duration_days <= 14:
        return 20 + ((duration_days - 7) / 7) * 20
    elif duration_days <= 30:
        return 40 + ((duration_days - 14) / 16) * 20
    elif duration_days <= 60:
        return 60 + ((duration_days - 30) / 30) * 20
    else:
        # Cap at 100, gradually approach 100 for very long running ads
        extra_score = min(20, (duration_days - 60) / 30 * 20)
        return 80 + extra_score


def calculate_impressions_score(
    impressions_lower: Optional[int],
    impressions_upper: Optional[int],
    max_impressions_mid: float
) -> float:
    """
    Calculate impressions score using log scale normalization (0-100).

    impressions_mid = (lower + upper) / 2
    score = (log(mid) / log(max)) * 100
    """
    if not impressions_lower and not impressions_upper:
        return 0

    lower = impressions_lower or 0
    upper = impressions_upper or lower
    impressions_mid = (lower + upper) / 2

    if impressions_mid <= 0:
        return 0

    if max_impressions_mid <= 1:
        return 100 if impressions_mid > 0 else 0

    # Log scale normalization
    log_mid = math.log(impressions_mid + 1)
    log_max = math.log(max_impressions_mid + 1)

    return min(100, (log_mid / log_max) * 100)


def calculate_total_score(duration_score: float, impressions_score: float) -> float:
    """
    Calculate total success score.

    Duration weight: 40%
    Impressions weight: 60%
    """
    return (duration_score * 0.4) + (impressions_score * 0.6)


async def get_max_impressions_mid(db: AsyncSession) -> float:
    """Get maximum impressions mid value from all ads."""
    result = await db.execute(
        select(
            func.max(
                (func.coalesce(AdRaw.impressions_lower, 0) +
                 func.coalesce(AdRaw.impressions_upper, 0)) / 2
            )
        )
    )
    max_mid = result.scalar()
    return max_mid or 1


async def calculate_ad_score(
    ad: AdRaw,
    max_impressions_mid: float
) -> dict:
    """Calculate success score for a single ad."""
    duration_score = calculate_duration_score(ad.duration_days)
    impressions_score = calculate_impressions_score(
        ad.impressions_lower,
        ad.impressions_upper,
        max_impressions_mid
    )
    total_score = calculate_total_score(duration_score, impressions_score)

    return {
        "duration_score": round(duration_score, 2),
        "impressions_score": round(impressions_score, 2),
        "total_score": round(total_score, 2),
    }


async def calculate_all_scores(db: AsyncSession) -> dict:
    """
    Calculate success scores for all ads.

    Returns statistics about the calculation.
    """
    # Get max impressions for normalization
    max_impressions_mid = await get_max_impressions_mid(db)

    # Get all ads
    result = await db.execute(select(AdRaw))
    ads = result.scalars().all()

    if not ads:
        return {"calculated": 0, "successful": 0}

    # Calculate scores for all ads
    scores = []
    for ad in ads:
        score_data = await calculate_ad_score(ad, max_impressions_mid)
        scores.append({
            "ad_id": ad.ad_id,
            **score_data
        })

    # Sort by total score to calculate percentiles
    scores.sort(key=lambda x: x["total_score"], reverse=True)
    total_ads = len(scores)

    # Assign percentiles and determine success
    for i, score in enumerate(scores):
        percentile = int(((total_ads - i) / total_ads) * 100)
        score["percentile"] = percentile
        score["is_successful"] = percentile >= 80  # Top 20%

    # Upsert scores to database
    calculated = 0
    successful = 0

    for score in scores:
        # Check if score exists
        result = await db.execute(
            select(AdSuccessScore).where(AdSuccessScore.ad_id == score["ad_id"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.duration_score = score["duration_score"]
            existing.impressions_score = score["impressions_score"]
            existing.total_score = score["total_score"]
            existing.percentile = score["percentile"]
            existing.is_successful = score["is_successful"]
            existing.calculated_at = datetime.utcnow()
        else:
            new_score = AdSuccessScore(
                ad_id=score["ad_id"],
                duration_score=score["duration_score"],
                impressions_score=score["impressions_score"],
                total_score=score["total_score"],
                percentile=score["percentile"],
                is_successful=score["is_successful"],
            )
            db.add(new_score)

        calculated += 1
        if score["is_successful"]:
            successful += 1

    await db.commit()

    return {
        "calculated": calculated,
        "successful": successful,
        "max_impressions_mid": max_impressions_mid,
    }


async def get_scoring_stats(db: AsyncSession) -> dict:
    """Get scoring statistics."""
    # Total count
    total_result = await db.execute(select(func.count()).select_from(AdSuccessScore))
    total = total_result.scalar() or 0

    # Successful count
    successful_result = await db.execute(
        select(func.count()).select_from(AdSuccessScore).where(AdSuccessScore.is_successful == True)
    )
    successful = successful_result.scalar() or 0

    # Average scores
    avg_result = await db.execute(
        select(
            func.avg(AdSuccessScore.total_score),
            func.avg(AdSuccessScore.duration_score),
            func.avg(AdSuccessScore.impressions_score),
            func.max(AdSuccessScore.total_score),
            func.min(AdSuccessScore.total_score),
        )
    )
    avg_row = avg_result.one_or_none()

    if avg_row and avg_row[0] is not None:
        avg_total, avg_duration, avg_impressions, max_score, min_score = avg_row
    else:
        avg_total = avg_duration = avg_impressions = max_score = min_score = 0

    return {
        "total_scored": total,
        "successful_count": successful,
        "success_rate": round((successful / total * 100) if total > 0 else 0, 2),
        "avg_total_score": round(float(avg_total or 0), 2),
        "avg_duration_score": round(float(avg_duration or 0), 2),
        "avg_impressions_score": round(float(avg_impressions or 0), 2),
        "max_score": round(float(max_score or 0), 2),
        "min_score": round(float(min_score or 0), 2),
    }
