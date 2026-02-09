"""Monitoring API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.ad import MonitoringKeyword, MonitoringRun, Notification
from app.workers.collect_task import collect_ads

router = APIRouter()


# Request/Response Models
class KeywordCreate(BaseModel):
    """Request model for creating a monitoring keyword."""
    keyword: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., min_length=1, max_length=50)
    country: str = Field(default="KR", max_length=10)
    schedule_cron: str = Field(default="0 9 * * *", max_length=50)


class KeywordUpdate(BaseModel):
    """Request model for updating a monitoring keyword."""
    keyword: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, min_length=1, max_length=50)
    country: Optional[str] = Field(None, max_length=10)
    schedule_cron: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class KeywordResponse(BaseModel):
    """Response model for a monitoring keyword."""
    id: int
    keyword: str
    industry: str
    country: str
    is_active: bool
    schedule_cron: str
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class RunResponse(BaseModel):
    """Response model for a monitoring run."""
    id: int
    keyword_id: int
    status: str
    new_ads_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """Response model for a notification."""
    id: int
    type: str
    title: str
    message: str
    extra_data: Optional[dict]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Keyword Endpoints
@router.post("/keywords", response_model=KeywordResponse, status_code=201)
async def create_keyword(
    data: KeywordCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new monitoring keyword."""
    keyword = MonitoringKeyword(
        keyword=data.keyword,
        industry=data.industry,
        country=data.country,
        schedule_cron=data.schedule_cron,
    )
    db.add(keyword)
    await db.commit()
    await db.refresh(keyword)
    return keyword


@router.get("/keywords", response_model=List[KeywordResponse])
async def list_keywords(
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
):
    """List all monitoring keywords."""
    query = select(MonitoringKeyword).order_by(MonitoringKeyword.created_at.desc())

    if is_active is not None:
        query = query.where(MonitoringKeyword.is_active == is_active)

    result = await db.execute(query)
    keywords = result.scalars().all()
    return keywords


@router.get("/keywords/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific monitoring keyword."""
    result = await db.execute(
        select(MonitoringKeyword).where(MonitoringKeyword.id == keyword_id)
    )
    keyword = result.scalar_one_or_none()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    return keyword


@router.put("/keywords/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    data: KeywordUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a monitoring keyword."""
    result = await db.execute(
        select(MonitoringKeyword).where(MonitoringKeyword.id == keyword_id)
    )
    keyword = result.scalar_one_or_none()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    if data.keyword is not None:
        keyword.keyword = data.keyword
    if data.industry is not None:
        keyword.industry = data.industry
    if data.country is not None:
        keyword.country = data.country
    if data.schedule_cron is not None:
        keyword.schedule_cron = data.schedule_cron
    if data.is_active is not None:
        keyword.is_active = data.is_active

    await db.commit()
    await db.refresh(keyword)
    return keyword


@router.delete("/keywords/{keyword_id}", status_code=204)
async def delete_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a monitoring keyword."""
    result = await db.execute(
        select(MonitoringKeyword).where(MonitoringKeyword.id == keyword_id)
    )
    keyword = result.scalar_one_or_none()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    await db.delete(keyword)
    await db.commit()
    return None


@router.post("/keywords/{keyword_id}/run", response_model=RunResponse)
async def run_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200, description="Number of ads to collect"),
):
    """Immediately run collection for a keyword."""
    result = await db.execute(
        select(MonitoringKeyword).where(MonitoringKeyword.id == keyword_id)
    )
    keyword = result.scalar_one_or_none()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    # Create run record
    run = MonitoringRun(
        keyword_id=keyword_id,
        status="pending",
        started_at=datetime.utcnow(),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Queue collection task
    collect_ads.delay(
        job_id=f"monitoring-{run.id}",
        keywords=[keyword.keyword],
        industry=keyword.industry,
        country=keyword.country,
        limit=limit,
    )

    # Update keyword last run
    keyword.last_run_at = datetime.utcnow()
    await db.commit()

    return run


@router.get("/keywords/{keyword_id}/runs", response_model=List[RunResponse])
async def list_keyword_runs(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
):
    """List recent runs for a keyword."""
    result = await db.execute(
        select(MonitoringRun)
        .where(MonitoringRun.keyword_id == keyword_id)
        .order_by(MonitoringRun.started_at.desc())
        .limit(limit)
    )
    runs = result.scalars().all()
    return runs


# Notification Endpoints
@router.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    unread_only: bool = Query(False, description="Only show unread notifications"),
    limit: int = Query(20, ge=1, le=100),
):
    """List notifications."""
    query = select(Notification).order_by(Notification.created_at.desc())

    if unread_only:
        query = query.where(Notification.is_read == False)

    query = query.limit(limit)

    result = await db.execute(query)
    notifications = result.scalars().all()
    return notifications


@router.get("/notifications/count")
async def get_notification_count(
    db: AsyncSession = Depends(get_db),
):
    """Get unread notification count."""
    result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.is_read == False)
    )
    count = result.scalar() or 0
    return {"unread_count": count}


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    await db.commit()

    return {"status": "ok"}


@router.put("/notifications/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    result = await db.execute(
        select(Notification).where(Notification.is_read == False)
    )
    notifications = result.scalars().all()

    for notification in notifications:
        notification.is_read = True

    await db.commit()

    return {"status": "ok", "marked_count": len(notifications)}
