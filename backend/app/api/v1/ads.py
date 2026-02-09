import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.ad import AdRaw, AdSuccessScore, CollectJob
from app.schemas.ad import (
    AdDetail,
    AdList,
    AdListResponse,
    CollectJobCreate,
    CollectJobResponse,
    CollectJobStatus,
    CopyAnalysisSummary,
    ImageAnalysisSummary,
    SuccessScoreSummary,
)
from app.workers.collect_task import collect_ads
from app.services.screenshot import capture_screenshot

router = APIRouter()


@router.post("/collect", response_model=CollectJobResponse, status_code=201)
async def create_collect_job(
    data: CollectJobCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new ad collection job.

    This will queue a background task to fetch ads from Meta Ad Library.
    """
    # Create job record
    job = CollectJob(
        keywords=data.keywords,
        industry=data.industry,
        country=data.country,
        target_count=data.limit,
        status="pending",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Queue Celery task
    collect_ads.delay(
        job_id=str(job.job_id),
        keywords=data.keywords,
        industry=data.industry,
        country=data.country,
        limit=data.limit,
    )

    # Estimate time (roughly 2 seconds per ad)
    estimated_time = data.limit * 2

    return CollectJobResponse(
        job_id=job.job_id,
        status=job.status,
        estimated_time=estimated_time,
    )


@router.get("/collect/{job_id}", response_model=CollectJobStatus)
async def get_collect_job_status(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the status of a collection job."""
    result = await db.execute(select(CollectJob).where(CollectJob.job_id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return CollectJobStatus(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        collected_count=job.collected_count,
        target_count=job.target_count,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )


@router.get("", response_model=AdListResponse)
async def list_ads(
    db: AsyncSession = Depends(get_db),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    region: Optional[str] = Query(None, description="Filter by region"),
    min_duration: Optional[int] = Query(None, ge=0, description="Minimum duration in days"),
    max_duration: Optional[int] = Query(None, ge=0, description="Maximum duration in days"),
    successful_only: bool = Query(False, description="Filter only successful ads (top 20%)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("-duration_days", description="Sort field (prefix with - for desc)"),
):
    """
    List ads with filtering and pagination.

    Supports filtering by industry, region, and duration.
    """
    # Base query
    query = select(AdRaw).options(
        selectinload(AdRaw.image_analysis),
        selectinload(AdRaw.copy_analysis),
        selectinload(AdRaw.success_score),
    )

    # Apply filters
    if industry:
        query = query.where(AdRaw.industry == industry)
    if region:
        query = query.where(AdRaw.region == region)
    if successful_only:
        query = query.join(AdSuccessScore).where(AdSuccessScore.is_successful == True)

    # Count query
    count_query = select(func.count()).select_from(AdRaw)
    if industry:
        count_query = count_query.where(AdRaw.industry == industry)
    if region:
        count_query = count_query.where(AdRaw.region == region)
    if successful_only:
        count_query = count_query.join(AdSuccessScore).where(AdSuccessScore.is_successful == True)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply sorting
    desc = sort.startswith("-")
    sort_field = sort.lstrip("-")

    if sort_field == "duration_days":
        # Sort by calculated duration (start_date)
        if desc:
            query = query.order_by(AdRaw.start_date.asc())  # Older = longer duration
        else:
            query = query.order_by(AdRaw.start_date.desc())
    elif sort_field == "collected_at":
        if desc:
            query = query.order_by(AdRaw.collected_at.desc())
        else:
            query = query.order_by(AdRaw.collected_at.asc())
    else:
        query = query.order_by(AdRaw.collected_at.desc())

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    ads = result.scalars().all()

    # Filter by duration in Python (since it's a computed property)
    if min_duration is not None or max_duration is not None:
        filtered_ads = []
        for ad in ads:
            duration = ad.duration_days
            if min_duration is not None and duration < min_duration:
                continue
            if max_duration is not None and duration > max_duration:
                continue
            filtered_ads.append(ad)
        ads = filtered_ads

    # Build response
    items = [
        AdList(
            id=ad.id,
            ad_id=ad.ad_id,
            page_name=ad.page_name,
            ad_creative_body=ad.ad_creative_body,
            start_date=ad.start_date,
            stop_date=ad.stop_date,
            duration_days=ad.duration_days,
            platforms=ad.platforms or [],
            industry=ad.industry,
            region=ad.region,
            image_url=ad.image_url,
            image_s3_path=ad.image_s3_path,
            has_image_analysis=ad.has_image_analysis,
            has_copy_analysis=ad.has_copy_analysis,
            collected_at=ad.collected_at,
            success_score=ad.success_score.total_score if ad.success_score else None,
            is_successful=ad.success_score.is_successful if ad.success_score else False,
        )
        for ad in ads
    ]

    pages = math.ceil(total / limit)

    return AdListResponse(
        items=items,
        total=total,
        page=page,
        pages=pages,
        has_next=page < pages,
    )


@router.delete("/{ad_id}", status_code=204)
async def delete_ad(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete an ad and its associated analysis data."""
    result = await db.execute(
        select(AdRaw).where(AdRaw.ad_id == ad_id)
    )
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    await db.delete(ad)
    await db.commit()

    return None


@router.get("/{ad_id}", response_model=AdDetail)
async def get_ad_detail(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific ad including analysis results."""
    result = await db.execute(
        select(AdRaw)
        .options(
            selectinload(AdRaw.image_analysis),
            selectinload(AdRaw.copy_analysis),
            selectinload(AdRaw.success_score),
        )
        .where(AdRaw.ad_id == ad_id)
    )
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    # Build image analysis summary
    image_analysis = None
    if ad.image_analysis:
        ia = ad.image_analysis
        image_analysis = ImageAnalysisSummary(
            composition={
                "has_person": ia.has_person,
                "person_type": ia.person_type,
                "text_ratio": ia.text_ratio,
                "has_chart": ia.has_chart,
                "logo_position": ia.logo_position,
            },
            colors={
                "primary": ia.primary_color,
                "secondary": ia.secondary_color,
                "tertiary": ia.tertiary_color,
                "tone": ia.color_tone,
                "saturation": ia.saturation,
            },
            layout={
                "type": ia.layout_type,
                "atmosphere": ia.atmosphere,
                "emphasis_elements": ia.emphasis_elements or [],
            },
            mentioned_regions=ia.mentioned_regions or [],
            analyzed_at=ia.analyzed_at,
        )

    # Build copy analysis summary
    copy_analysis = None
    if ad.copy_analysis:
        ca = ad.copy_analysis
        copy_analysis = CopyAnalysisSummary(
            structure={
                "headline": ca.headline,
                "headline_length": ca.headline_length,
                "body": ca.body,
                "cta": ca.cta,
                "core_message": ca.core_message,
            },
            numbers=ca.numbers or [],
            offer={
                "discount_info": ca.discount_info,
                "free_benefit": ca.free_benefit,
                "social_proof": ca.social_proof,
                "urgency": ca.urgency,
                "differentiation": ca.differentiation,
            },
            tone={
                "formality": ca.formality,
                "emotion": ca.emotion,
                "style": ca.style,
            },
            target_audience=ca.target_audience,
            keywords=ca.keywords or [],
            regions=ca.regions or [],
            analyzed_at=ca.analyzed_at,
        )

    # Build success score summary
    success_score_detail = None
    if ad.success_score:
        ss = ad.success_score
        success_score_detail = SuccessScoreSummary(
            duration_score=ss.duration_score,
            impressions_score=ss.impressions_score,
            total_score=ss.total_score,
            percentile=ss.percentile,
            is_successful=ss.is_successful,
            calculated_at=ss.calculated_at,
        )

    return AdDetail(
        id=ad.id,
        ad_id=ad.ad_id,
        page_name=ad.page_name,
        ad_creative_body=ad.ad_creative_body,
        ad_creative_link_title=ad.ad_creative_link_title,
        ad_creative_link_description=ad.ad_creative_link_description,
        ad_snapshot_url=ad.ad_snapshot_url,
        start_date=ad.start_date,
        stop_date=ad.stop_date,
        duration_days=ad.duration_days,
        platforms=ad.platforms or [],
        industry=ad.industry,
        region=ad.region,
        currency=ad.currency,
        spend_lower=ad.spend_lower,
        spend_upper=ad.spend_upper,
        impressions_lower=ad.impressions_lower,
        impressions_upper=ad.impressions_upper,
        target_country=ad.target_country,
        image_url=ad.image_url,
        image_s3_path=ad.image_s3_path,
        has_image_analysis=ad.has_image_analysis,
        has_copy_analysis=ad.has_copy_analysis,
        collected_at=ad.collected_at,
        image_analysis=image_analysis,
        copy_analysis=copy_analysis,
        success_score=ad.success_score.total_score if ad.success_score else None,
        is_successful=ad.success_score.is_successful if ad.success_score else False,
        success_score_detail=success_score_detail,
    )


@router.post("/{ad_id}/screenshot")
async def capture_ad_screenshot(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Capture screenshot of an ad's render page."""
    result = await db.execute(
        select(AdRaw).where(AdRaw.ad_id == ad_id)
    )
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    if not ad.image_url or '/ads/archive/render_ad/' not in ad.image_url:
        raise HTTPException(status_code=400, detail="No render URL available")

    # Capture screenshot
    screenshot_path = await capture_screenshot(ad.image_url, ad.ad_id)

    if not screenshot_path:
        raise HTTPException(status_code=500, detail="Failed to capture screenshot")

    # Update ad with local image path
    ad.image_s3_path = screenshot_path
    await db.commit()

    return {"screenshot_url": screenshot_path}


@router.post("/screenshots/batch")
async def capture_screenshots_batch(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Number of ads to process"),
):
    """Capture screenshots for ads that don't have one yet."""
    # Find ads with render_ad URLs but no screenshot
    result = await db.execute(
        select(AdRaw)
        .where(AdRaw.image_url.ilike('%/ads/archive/render_ad/%'))
        .where(AdRaw.image_s3_path.is_(None))
        .limit(limit)
    )
    ads = result.scalars().all()

    captured = 0
    failed = 0

    for ad in ads:
        screenshot_path = await capture_screenshot(ad.image_url, ad.ad_id)
        if screenshot_path:
            ad.image_s3_path = screenshot_path
            captured += 1
        else:
            failed += 1

    await db.commit()

    return {
        "processed": len(ads),
        "captured": captured,
        "failed": failed,
    }
