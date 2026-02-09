import uuid
from datetime import date, datetime
from typing import Any, List, Optional

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AdRaw(Base):
    """Raw ad data collected from Meta Ad Library."""

    __tablename__ = "ads_raw"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    page_name: Mapped[Optional[str]] = mapped_column(String(255))
    page_id: Mapped[Optional[str]] = mapped_column(String(255))
    ad_creative_body: Mapped[Optional[str]] = mapped_column(Text)
    ad_creative_link_title: Mapped[Optional[str]] = mapped_column(Text)
    ad_creative_link_description: Mapped[Optional[str]] = mapped_column(Text)
    ad_snapshot_url: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    stop_date: Mapped[Optional[date]] = mapped_column(Date)
    platforms: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    spend_lower: Mapped[Optional[int]] = mapped_column(Integer)
    spend_upper: Mapped[Optional[int]] = mapped_column(Integer)
    impressions_lower: Mapped[Optional[int]] = mapped_column(Integer)
    impressions_upper: Mapped[Optional[int]] = mapped_column(Integer)
    target_country: Mapped[str] = mapped_column(String(10), default="KR")
    industry: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text)
    image_s3_path: Mapped[Optional[str]] = mapped_column(Text)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    image_analysis: Mapped[Optional["AdsAnalysisImage"]] = relationship(
        "AdsAnalysisImage", back_populates="ad", uselist=False, lazy="joined",
        cascade="all, delete-orphan", passive_deletes=True
    )
    copy_analysis: Mapped[Optional["AdsAnalysisCopy"]] = relationship(
        "AdsAnalysisCopy", back_populates="ad", uselist=False, lazy="joined",
        cascade="all, delete-orphan", passive_deletes=True
    )
    success_score: Mapped[Optional["AdSuccessScore"]] = relationship(
        "AdSuccessScore", back_populates="ad", uselist=False, lazy="joined",
        cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def duration_days(self) -> int:
        """Calculate duration in days."""
        if self.start_date is None:
            return 0
        end = self.stop_date or date.today()
        return (end - self.start_date).days

    @property
    def has_image_analysis(self) -> bool:
        """Check if image analysis exists."""
        return self.image_analysis is not None

    @property
    def has_copy_analysis(self) -> bool:
        """Check if copy analysis exists."""
        return self.copy_analysis is not None

    @property
    def has_success_score(self) -> bool:
        """Check if success score exists."""
        return self.success_score is not None


class AdsAnalysisImage(Base):
    """Image analysis results from Claude Vision."""

    __tablename__ = "ads_analysis_image"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("ads_raw.ad_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Composition
    has_person: Mapped[Optional[bool]] = mapped_column(Boolean)
    person_type: Mapped[Optional[str]] = mapped_column(String(50))
    text_ratio: Mapped[Optional[int]] = mapped_column(Integer)
    has_chart: Mapped[Optional[bool]] = mapped_column(Boolean)
    logo_position: Mapped[Optional[str]] = mapped_column(String(50))

    # Colors
    primary_color: Mapped[Optional[str]] = mapped_column(String(7))
    secondary_color: Mapped[Optional[str]] = mapped_column(String(7))
    tertiary_color: Mapped[Optional[str]] = mapped_column(String(7))
    color_tone: Mapped[Optional[str]] = mapped_column(String(20))
    saturation: Mapped[Optional[str]] = mapped_column(String(20))

    # Layout
    layout_type: Mapped[Optional[str]] = mapped_column(String(50))
    atmosphere: Mapped[Optional[str]] = mapped_column(String(50))
    emphasis_elements: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    mentioned_regions: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Raw response
    analysis_raw: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    ad: Mapped["AdRaw"] = relationship("AdRaw", back_populates="image_analysis")


class AdsAnalysisCopy(Base):
    """Copy analysis results from Claude."""

    __tablename__ = "ads_analysis_copy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("ads_raw.ad_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Structure
    headline: Mapped[Optional[str]] = mapped_column(Text)
    headline_length: Mapped[Optional[int]] = mapped_column(Integer)
    body: Mapped[Optional[str]] = mapped_column(Text)
    cta: Mapped[Optional[str]] = mapped_column(Text)
    core_message: Mapped[Optional[str]] = mapped_column(String(50))

    # Numbers and regions
    numbers: Mapped[Optional[dict]] = mapped_column(JSON)
    regions: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Offer
    discount_info: Mapped[Optional[str]] = mapped_column(String(255))
    free_benefit: Mapped[Optional[str]] = mapped_column(String(255))
    social_proof: Mapped[Optional[str]] = mapped_column(String(255))
    urgency: Mapped[Optional[str]] = mapped_column(String(255))
    differentiation: Mapped[Optional[str]] = mapped_column(Text)

    # Tone
    formality: Mapped[Optional[str]] = mapped_column(String(20))
    emotion: Mapped[Optional[str]] = mapped_column(String(20))
    style: Mapped[Optional[str]] = mapped_column(String(20))

    # Target and keywords
    target_audience: Mapped[Optional[str]] = mapped_column(String(50))
    keywords: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Raw response
    analysis_raw: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    ad: Mapped["AdRaw"] = relationship("AdRaw", back_populates="copy_analysis")


class AdSuccessScore(Base):
    """Success score for ads based on duration and impressions."""

    __tablename__ = "ads_success_score"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("ads_raw.ad_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    duration_score: Mapped[float] = mapped_column(Float, default=0)
    impressions_score: Mapped[float] = mapped_column(Float, default=0)
    total_score: Mapped[float] = mapped_column(Float, default=0)
    percentile: Mapped[int] = mapped_column(Integer, default=0)
    is_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship
    ad: Mapped["AdRaw"] = relationship("AdRaw", back_populates="success_score")


class PatternAnalysis(Base):
    """Pattern analysis results comparing successful vs general ads."""

    __tablename__ = "pattern_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'image' | 'copy'
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_value: Mapped[str] = mapped_column(String(255), nullable=False)
    successful_count: Mapped[int] = mapped_column(Integer, default=0)
    successful_ratio: Mapped[float] = mapped_column(Float, default=0)
    general_count: Mapped[int] = mapped_column(Integer, default=0)
    general_ratio: Mapped[float] = mapped_column(Float, default=0)
    lift: Mapped[float] = mapped_column(Float, default=0)
    is_pattern: Mapped[bool] = mapped_column(Boolean, default=False)
    industry: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PatternInsight(Base):
    """AI-generated insights from pattern analysis."""

    __tablename__ = "pattern_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'formula' | 'recommendation'
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_patterns: Mapped[Optional[dict]] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    industry: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MonitoringKeyword(Base):
    """Keywords for automatic monitoring."""

    __tablename__ = "monitoring_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(10), default="KR")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    schedule_cron: Mapped[str] = mapped_column(String(50), default="0 9 * * *")
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship
    runs: Mapped[List["MonitoringRun"]] = relationship(
        "MonitoringRun", back_populates="keyword", cascade="all, delete-orphan"
    )


class MonitoringRun(Base):
    """Execution history for monitoring keywords."""

    __tablename__ = "monitoring_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword_id: Mapped[int] = mapped_column(Integer, ForeignKey("monitoring_keywords.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    new_ads_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Relationship
    keyword: Mapped["MonitoringKeyword"] = relationship("MonitoringKeyword", back_populates="runs")


class Notification(Base):
    """User notifications."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CollectJob(Base):
    """Collection job status tracking."""

    __tablename__ = "collect_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")
    keywords: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    industry: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(10), default="KR")
    target_count: Mapped[Optional[int]] = mapped_column(Integer)
    collected_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def progress(self) -> int:
        """Calculate progress percentage."""
        if self.target_count is None or self.target_count == 0:
            return 0
        return min(100, int((self.collected_count / self.target_count) * 100))
