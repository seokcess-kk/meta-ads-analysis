from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Image Analysis
class CompositionSchema(BaseModel):
    """Image composition analysis."""

    has_person: bool = False
    person_type: Optional[str] = None
    text_ratio: int = 0
    has_chart: bool = False
    logo_position: Optional[str] = None


class ColorsSchema(BaseModel):
    """Image color analysis."""

    primary: Optional[str] = None
    secondary: Optional[str] = None
    tertiary: Optional[str] = None
    tone: Optional[str] = None
    saturation: Optional[str] = None


class LayoutSchema(BaseModel):
    """Image layout analysis."""

    type: Optional[str] = None
    atmosphere: Optional[str] = None
    emphasis_elements: List[str] = []


class ImageAnalysisResponse(BaseModel):
    """Response schema for image analysis."""

    id: int
    ad_id: str
    composition: CompositionSchema
    colors: ColorsSchema
    layout: LayoutSchema
    mentioned_regions: List[str] = []
    analyzed_at: datetime

    class Config:
        from_attributes = True


# Copy Analysis
class StructureSchema(BaseModel):
    """Copy structure analysis."""

    headline: Optional[str] = None
    headline_length: int = 0
    body: Optional[str] = None
    cta: Optional[str] = None
    core_message: Optional[str] = None


class NumberSchema(BaseModel):
    """Number information in copy."""

    value: float
    unit: str
    context: str


class OfferSchema(BaseModel):
    """Offer analysis in copy."""

    discount_info: Optional[str] = None
    free_benefit: Optional[str] = None
    social_proof: Optional[str] = None
    urgency: Optional[str] = None
    differentiation: Optional[str] = None


class ToneSchema(BaseModel):
    """Tone analysis in copy."""

    formality: Optional[str] = None
    emotion: Optional[str] = None
    style: Optional[str] = None


class CopyAnalysisResponse(BaseModel):
    """Response schema for copy analysis."""

    id: int
    ad_id: str
    structure: StructureSchema
    numbers: List[NumberSchema] = []
    offer: OfferSchema
    tone: ToneSchema
    target_audience: Optional[str] = None
    keywords: List[str] = []
    regions: List[str] = []
    analyzed_at: datetime

    class Config:
        from_attributes = True


# Queue Response
class AnalysisQueueResponse(BaseModel):
    """Response when analysis is queued."""

    status: str = "queued"
    message: str


# Batch Request/Response
class AnalysisBatchRequest(BaseModel):
    """Request for batch analysis."""

    ad_ids: List[str] = Field(..., max_length=50, description="Ad IDs to analyze")
    types: List[str] = Field(
        default=["image", "copy"],
        description="Analysis types: image, copy",
    )


class AnalysisBatchResponse(BaseModel):
    """Response for batch analysis."""

    queued_count: int
    skipped_count: int
    message: str
