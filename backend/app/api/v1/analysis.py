from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.ad import AdRaw, AdsAnalysisCopy, AdsAnalysisImage
from app.schemas.analysis import (
    AnalysisBatchRequest,
    AnalysisBatchResponse,
    AnalysisQueueResponse,
)
from app.workers.analyze_task import analyze_batch, analyze_copy, analyze_image

router = APIRouter()


@router.post("/image/{ad_id}", response_model=AnalysisQueueResponse, status_code=202)
async def queue_image_analysis(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Queue image analysis for an ad.

    The analysis will be processed in the background.
    """
    # Check if ad exists
    result = await db.execute(select(AdRaw).where(AdRaw.ad_id == ad_id))
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    if not ad.image_url and not ad.ad_snapshot_url:
        raise HTTPException(status_code=400, detail="No image URL for this ad")

    # Check if already analyzed
    existing = await db.execute(
        select(AdsAnalysisImage).where(AdsAnalysisImage.ad_id == ad_id)
    )
    if existing.scalar_one_or_none():
        return AnalysisQueueResponse(
            status="already_analyzed",
            message="Image analysis already exists for this ad",
        )

    # Queue task
    analyze_image.delay(ad_id)

    return AnalysisQueueResponse(
        status="queued",
        message="Image analysis queued successfully",
    )


@router.post("/copy/{ad_id}", response_model=AnalysisQueueResponse, status_code=202)
async def queue_copy_analysis(
    ad_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Queue copy analysis for an ad.

    The analysis will be processed in the background.
    """
    # Check if ad exists
    result = await db.execute(select(AdRaw).where(AdRaw.ad_id == ad_id))
    ad = result.scalar_one_or_none()

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    if not ad.ad_creative_body and not ad.ad_creative_link_title:
        raise HTTPException(status_code=400, detail="No copy text for this ad")

    # Check if already analyzed
    existing = await db.execute(
        select(AdsAnalysisCopy).where(AdsAnalysisCopy.ad_id == ad_id)
    )
    if existing.scalar_one_or_none():
        return AnalysisQueueResponse(
            status="already_analyzed",
            message="Copy analysis already exists for this ad",
        )

    # Queue task
    analyze_copy.delay(ad_id)

    return AnalysisQueueResponse(
        status="queued",
        message="Copy analysis queued successfully",
    )


@router.post("/batch", response_model=AnalysisBatchResponse, status_code=202)
async def queue_batch_analysis(
    data: AnalysisBatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Queue analysis for multiple ads.

    Ads that already have analysis will be skipped.
    """
    queued_ids: List[str] = []
    skipped_count = 0

    for ad_id in data.ad_ids:
        # Check if ad exists
        result = await db.execute(select(AdRaw).where(AdRaw.ad_id == ad_id))
        ad = result.scalar_one_or_none()

        if not ad:
            skipped_count += 1
            continue

        # Check which analyses are needed
        needs_image = "image" in data.types
        needs_copy = "copy" in data.types

        if needs_image:
            existing = await db.execute(
                select(AdsAnalysisImage).where(AdsAnalysisImage.ad_id == ad_id)
            )
            if existing.scalar_one_or_none():
                needs_image = False

        if needs_copy:
            existing = await db.execute(
                select(AdsAnalysisCopy).where(AdsAnalysisCopy.ad_id == ad_id)
            )
            if existing.scalar_one_or_none():
                needs_copy = False

        if needs_image or needs_copy:
            queued_ids.append(ad_id)
        else:
            skipped_count += 1

    # Queue batch task if there are ads to analyze
    if queued_ids:
        analyze_batch.delay(queued_ids, data.types)

    return AnalysisBatchResponse(
        queued_count=len(queued_ids),
        skipped_count=skipped_count,
        message=f"Queued {len(queued_ids)} ads for analysis, skipped {skipped_count}",
    )
