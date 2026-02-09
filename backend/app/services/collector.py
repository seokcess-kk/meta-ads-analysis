import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

META_AD_LIBRARY_URL = "https://graph.facebook.com/v18.0/ads_archive"


class MetaAdCollector:
    """Collector for Meta Ad Library API."""

    def __init__(self):
        self.access_token = settings.meta_access_token
        self.base_url = META_AD_LIBRARY_URL

    async def search_ads(
        self,
        search_terms: List[str],
        country: str = "KR",
        limit: int = 50,
        ad_reached_countries: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search ads from Meta Ad Library.

        Args:
            search_terms: List of search keywords
            country: Country code (default: KR)
            limit: Maximum number of ads to fetch
            ad_reached_countries: Countries where ad was shown

        Returns:
            List of ad data dictionaries
        """
        all_ads = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for term in search_terms:
                try:
                    ads = await self._fetch_ads_for_term(
                        client=client,
                        search_term=term,
                        country=country,
                        limit=limit - len(all_ads),
                        ad_reached_countries=ad_reached_countries,
                    )
                    all_ads.extend(ads)

                    if len(all_ads) >= limit:
                        break

                except Exception as e:
                    logger.error(f"Error fetching ads for term '{term}': {e}")
                    continue

        return all_ads[:limit]

    async def _fetch_ads_for_term(
        self,
        client: httpx.AsyncClient,
        search_term: str,
        country: str,
        limit: int,
        ad_reached_countries: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch ads for a single search term."""
        params = {
            "access_token": self.access_token,
            "search_terms": search_term,
            "ad_type": "ALL",
            "ad_reached_countries": ad_reached_countries or [country],
            "ad_active_status": "ALL",
            "fields": ",".join(
                [
                    "id",
                    "ad_creation_time",
                    "ad_delivery_start_time",
                    "ad_delivery_stop_time",
                    "ad_creative_bodies",
                    "ad_creative_link_captions",
                    "ad_creative_link_descriptions",
                    "ad_creative_link_titles",
                    "ad_snapshot_url",
                    "page_id",
                    "page_name",
                    "publisher_platforms",
                    "currency",
                    "spend",
                    "impressions",
                ]
            ),
            "limit": min(limit, 100),  # API max is 100 per request
        }

        ads = []
        next_url = self.base_url

        while next_url and len(ads) < limit:
            try:
                if next_url == self.base_url:
                    response = await client.get(next_url, params=params)
                else:
                    response = await client.get(next_url)

                response.raise_for_status()
                data = response.json()

                batch_ads = data.get("data", [])
                for ad in batch_ads:
                    parsed_ad = self._parse_ad(ad)
                    if parsed_ad:
                        ads.append(parsed_ad)

                # Get next page
                paging = data.get("paging", {})
                next_url = paging.get("next")

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                break
            except Exception as e:
                logger.error(f"Error fetching ads: {e}")
                break

        return ads

    def _parse_ad(self, raw_ad: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse raw ad data from API response."""
        try:
            # Extract creative bodies (can be multiple)
            bodies = raw_ad.get("ad_creative_bodies", [])
            body = bodies[0] if bodies else None

            # Extract link titles
            titles = raw_ad.get("ad_creative_link_titles", [])
            title = titles[0] if titles else None

            # Extract link descriptions
            descriptions = raw_ad.get("ad_creative_link_descriptions", [])
            description = descriptions[0] if descriptions else None

            # Parse dates
            start_date = None
            stop_date = None

            if raw_ad.get("ad_delivery_start_time"):
                start_date = datetime.fromisoformat(
                    raw_ad["ad_delivery_start_time"].replace("Z", "+00:00")
                ).date()

            if raw_ad.get("ad_delivery_stop_time"):
                stop_date = datetime.fromisoformat(
                    raw_ad["ad_delivery_stop_time"].replace("Z", "+00:00")
                ).date()

            # Parse spend
            spend = raw_ad.get("spend", {})
            spend_lower = None
            spend_upper = None
            if spend:
                spend_lower = spend.get("lower_bound")
                spend_upper = spend.get("upper_bound")

            # Parse impressions
            impressions = raw_ad.get("impressions", {})
            impressions_lower = None
            impressions_upper = None
            if impressions:
                impressions_lower = impressions.get("lower_bound")
                impressions_upper = impressions.get("upper_bound")

            return {
                "ad_id": raw_ad.get("id"),
                "page_id": raw_ad.get("page_id"),
                "page_name": raw_ad.get("page_name"),
                "ad_creative_body": body,
                "ad_creative_link_title": title,
                "ad_creative_link_description": description,
                "ad_snapshot_url": raw_ad.get("ad_snapshot_url"),
                "start_date": start_date,
                "stop_date": stop_date,
                "platforms": raw_ad.get("publisher_platforms", []),
                "currency": raw_ad.get("currency"),
                "spend_lower": spend_lower,
                "spend_upper": spend_upper,
                "impressions_lower": impressions_lower,
                "impressions_upper": impressions_upper,
            }

        except Exception as e:
            logger.error(f"Error parsing ad: {e}")
            return None

    async def get_ad_snapshot(self, snapshot_url: str) -> Optional[bytes]:
        """
        Download ad snapshot image.

        Args:
            snapshot_url: URL of the ad snapshot

        Returns:
            Image bytes or None if failed
        """
        if not snapshot_url:
            return None

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(snapshot_url)
                response.raise_for_status()
                return response.content
            except Exception as e:
                logger.error(f"Error downloading snapshot: {e}")
                return None


# Singleton instance
collector = MetaAdCollector()
