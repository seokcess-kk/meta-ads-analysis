import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude import claude_client
from app.models.ad import AdRaw, AdsAnalysisCopy, AdsAnalysisImage

logger = logging.getLogger(__name__)


class AdAnalyzer:
    """Service for analyzing ads using Claude AI."""

    async def analyze_image(
        self, db: AsyncSession, ad_id: str
    ) -> Optional[AdsAnalysisImage]:
        """
        Analyze ad image and store results.

        Args:
            db: Database session
            ad_id: Ad ID to analyze

        Returns:
            Analysis record or None if failed
        """
        # Get ad
        result = await db.execute(select(AdRaw).where(AdRaw.ad_id == ad_id))
        ad = result.scalar_one_or_none()

        if not ad:
            logger.error(f"Ad not found: {ad_id}")
            return None

        if not ad.image_url and not ad.ad_snapshot_url:
            logger.error(f"No image URL for ad: {ad_id}")
            return None

        image_url = ad.image_url or ad.ad_snapshot_url

        # Check if already analyzed
        existing = await db.execute(
            select(AdsAnalysisImage).where(AdsAnalysisImage.ad_id == ad_id)
        )
        if existing.scalar_one_or_none():
            logger.info(f"Image analysis already exists for ad: {ad_id}")
            return None

        # Call Claude API
        analysis_result = await claude_client.analyze_image(image_url)

        if not analysis_result:
            logger.error(f"Failed to analyze image for ad: {ad_id}")
            return None

        # Create analysis record
        analysis = self._create_image_analysis(ad_id, analysis_result)

        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

        logger.info(f"Image analysis completed for ad: {ad_id}")
        return analysis

    async def analyze_copy(
        self, db: AsyncSession, ad_id: str
    ) -> Optional[AdsAnalysisCopy]:
        """
        Analyze ad copy and store results.

        Args:
            db: Database session
            ad_id: Ad ID to analyze

        Returns:
            Analysis record or None if failed
        """
        # Get ad
        result = await db.execute(select(AdRaw).where(AdRaw.ad_id == ad_id))
        ad = result.scalar_one_or_none()

        if not ad:
            logger.error(f"Ad not found: {ad_id}")
            return None

        if not ad.ad_creative_body and not ad.ad_creative_link_title:
            logger.error(f"No copy text for ad: {ad_id}")
            return None

        # Check if already analyzed
        existing = await db.execute(
            select(AdsAnalysisCopy).where(AdsAnalysisCopy.ad_id == ad_id)
        )
        if existing.scalar_one_or_none():
            logger.info(f"Copy analysis already exists for ad: {ad_id}")
            return None

        # Call Claude API
        analysis_result = await claude_client.analyze_copy(
            body=ad.ad_creative_body,
            title=ad.ad_creative_link_title,
        )

        if not analysis_result:
            logger.error(f"Failed to analyze copy for ad: {ad_id}")
            return None

        # Create analysis record
        analysis = self._create_copy_analysis(ad_id, analysis_result)

        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

        logger.info(f"Copy analysis completed for ad: {ad_id}")
        return analysis

    def _create_image_analysis(
        self, ad_id: str, result: Dict[str, Any]
    ) -> AdsAnalysisImage:
        """Create image analysis record from Claude response."""
        composition = result.get("composition", {})
        colors = result.get("colors", {})
        layout = result.get("layout", {})

        return AdsAnalysisImage(
            ad_id=ad_id,
            # Composition
            has_person=composition.get("has_person"),
            person_type=composition.get("person_type"),
            text_ratio=composition.get("text_ratio"),
            has_chart=composition.get("has_chart"),
            logo_position=composition.get("logo_position"),
            # Colors
            primary_color=colors.get("primary"),
            secondary_color=colors.get("secondary"),
            tertiary_color=colors.get("tertiary"),
            color_tone=colors.get("tone"),
            saturation=colors.get("saturation"),
            # Layout
            layout_type=layout.get("type"),
            atmosphere=layout.get("atmosphere"),
            emphasis_elements=layout.get("emphasis_elements", []),
            # Regions
            mentioned_regions=result.get("mentioned_regions", []),
            # Raw
            analysis_raw=result,
            analyzed_at=datetime.utcnow(),
        )

    def _create_copy_analysis(
        self, ad_id: str, result: Dict[str, Any]
    ) -> AdsAnalysisCopy:
        """Create copy analysis record from Claude response."""
        structure = result.get("structure", {})
        offer = result.get("offer", {})
        tone = result.get("tone", {})

        return AdsAnalysisCopy(
            ad_id=ad_id,
            # Structure
            headline=structure.get("headline"),
            headline_length=structure.get("headline_length"),
            body=structure.get("body"),
            cta=structure.get("cta"),
            core_message=structure.get("core_message"),
            # Numbers
            numbers=result.get("numbers", []),
            # Regions
            regions=result.get("regions", []),
            # Offer
            discount_info=offer.get("discount_info"),
            free_benefit=offer.get("free_benefit"),
            social_proof=offer.get("social_proof"),
            urgency=offer.get("urgency"),
            differentiation=offer.get("differentiation"),
            # Tone
            formality=tone.get("formality"),
            emotion=tone.get("emotion"),
            style=tone.get("style"),
            # Target and keywords
            target_audience=result.get("target_audience"),
            keywords=result.get("keywords", []),
            # Raw
            analysis_raw=result,
            analyzed_at=datetime.utcnow(),
        )


# Singleton instance
analyzer = AdAnalyzer()
