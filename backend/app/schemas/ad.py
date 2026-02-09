from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AdBase(BaseModel):
    """Base schema for Ad."""

    ad_id: str
    page_name: Optional[str] = None
    page_id: Optional[str] = None
    ad_creative_body: Optional[str] = None
    ad_creative_link_title: Optional[str] = None
    ad_snapshot_url: Optional[str] = None
    start_date: Optional[date] = None
    stop_date: Optional[date] = None
    platforms: List[str] = []
    industry: str
    region: Optional[str] = None
    image_url: Optional[str] = None


class AdCreate(AdBase):
    """Schema for creating an Ad."""

    image_s3_path: Optional[str] = None


class AdList(BaseModel):
    """Schema for Ad in list view."""

    id: int
    ad_id: str
    page_name: Optional[str] = None
    ad_creative_body: Optional[str] = None
    start_date: Optional[date] = None
    stop_date: Optional[date] = None
    duration_days: int
    platforms: List[str] = []
    industry: str
    region: Optional[str] = None
    image_url: Optional[str] = None
    image_s3_path: Optional[str] = None
    has_image_analysis: bool = False
    has_copy_analysis: bool = False
    collected_at: datetime

    class Config:
        from_attributes = True


class ImageAnalysisSummary(BaseModel):
    """Summary of image analysis for detail view."""

    composition: dict
    colors: dict
    layout: dict
    mentioned_regions: List[str] = []
    analyzed_at: datetime

    class Config:
        from_attributes = True


class CopyAnalysisSummary(BaseModel):
    """Summary of copy analysis for detail view."""

    structure: dict
    numbers: Optional[List[dict]] = []
    offer: dict
    tone: dict
    target_audience: Optional[str] = None
    keywords: List[str] = []
    regions: List[str] = []
    analyzed_at: datetime

    class Config:
        from_attributes = True


class AdDetail(AdList):
    """Schema for Ad detail view with analysis."""

    ad_creative_link_title: Optional[str] = None
    ad_creative_link_description: Optional[str] = None
    ad_snapshot_url: Optional[str] = None
    currency: Optional[str] = None
    spend_lower: Optional[int] = None
    spend_upper: Optional[int] = None
    impressions_lower: Optional[int] = None
    impressions_upper: Optional[int] = None
    target_country: str = "KR"
    image_analysis: Optional[ImageAnalysisSummary] = None
    copy_analysis: Optional[CopyAnalysisSummary] = None

    class Config:
        from_attributes = True


class AdListResponse(BaseModel):
    """Paginated response for Ad list."""

    items: List[AdList]
    total: int
    page: int
    pages: int
    has_next: bool


# Collect Job Schemas
class CollectJobCreate(BaseModel):
    """Schema for creating a collect job."""

    keywords: List[str] = Field(..., min_length=1, description="Search keywords")
    industry: str = Field(..., description="Industry category")
    country: str = Field(default="KR", description="Country code")
    limit: int = Field(default=50, ge=1, le=200, description="Target count")


class CollectJobStatus(BaseModel):
    """Schema for collect job status."""

    job_id: UUID
    status: str
    progress: int
    collected_count: int
    target_count: Optional[int]
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CollectJobResponse(BaseModel):
    """Schema for collect job creation response."""

    job_id: UUID
    status: str
    estimated_time: int = Field(description="Estimated time in seconds")

    class Config:
        from_attributes = True
