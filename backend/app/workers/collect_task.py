import asyncio
import logging
from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.ad import AdRaw, CollectJob
from app.services.collector import collector
from app.services.storage import storage
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Create async engine for task
engine = create_async_engine(settings.async_database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def run_async(coro):
    """Run async coroutine in sync context."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If loop is already running, create new loop
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return loop.run_until_complete(coro)


@celery_app.task(bind=True, name="app.workers.collect_task.collect_ads")
def collect_ads(
    self,
    job_id: str,
    keywords: List[str],
    industry: str,
    country: str = "KR",
    limit: int = 50,
):
    """
    Celery task to collect ads from Meta Ad Library.

    Args:
        job_id: UUID of the collect job
        keywords: Search keywords
        industry: Industry category
        country: Country code
        limit: Target number of ads to collect
    """
    logger.info(f"Starting collect task for job {job_id}")

    try:
        run_async(_collect_ads_async(job_id, keywords, industry, country, limit))
    except Exception as e:
        logger.error(f"Collect task failed: {e}")
        run_async(_update_job_status(job_id, "failed", str(e)))
        raise


async def _collect_ads_async(
    job_id: str,
    keywords: List[str],
    industry: str,
    country: str,
    limit: int,
):
    """Async implementation of ad collection."""
    async with async_session() as session:
        # Update job status to running
        await _update_job_status_db(session, job_id, "running")

        try:
            # Fetch ads from Meta API
            ads_data = await collector.search_ads(
                search_terms=keywords,
                country=country,
                limit=limit,
            )

            logger.info(f"Fetched {len(ads_data)} ads from Meta API")

            collected_count = 0

            for ad_data in ads_data:
                try:
                    # Check if ad already exists
                    existing = await session.execute(
                        select(AdRaw).where(AdRaw.ad_id == ad_data["ad_id"])
                    )
                    if existing.scalar_one_or_none():
                        logger.debug(f"Ad {ad_data['ad_id']} already exists, skipping")
                        continue

                    # Download and upload image if available
                    image_s3_path = None
                    if ad_data.get("ad_snapshot_url"):
                        image_bytes = await collector.get_ad_snapshot(
                            ad_data["ad_snapshot_url"]
                        )
                        if image_bytes:
                            image_s3_path = storage.upload_image(
                                image_bytes, ad_data["ad_id"]
                            )
                            ad_data["image_url"] = ad_data["ad_snapshot_url"]

                    # Helper to convert to int safely
                    def to_int(val):
                        if val is None:
                            return None
                        try:
                            return int(val)
                        except (ValueError, TypeError):
                            return None

                    # Create ad record
                    ad = AdRaw(
                        ad_id=ad_data["ad_id"],
                        page_id=ad_data.get("page_id"),
                        page_name=ad_data.get("page_name"),
                        ad_creative_body=ad_data.get("ad_creative_body"),
                        ad_creative_link_title=ad_data.get("ad_creative_link_title"),
                        ad_creative_link_description=ad_data.get(
                            "ad_creative_link_description"
                        ),
                        ad_snapshot_url=ad_data.get("ad_snapshot_url"),
                        start_date=ad_data.get("start_date"),
                        stop_date=ad_data.get("stop_date"),
                        platforms=ad_data.get("platforms", []),
                        currency=ad_data.get("currency"),
                        spend_lower=to_int(ad_data.get("spend_lower")),
                        spend_upper=to_int(ad_data.get("spend_upper")),
                        impressions_lower=to_int(ad_data.get("impressions_lower")),
                        impressions_upper=to_int(ad_data.get("impressions_upper")),
                        industry=industry,
                        image_url=ad_data.get("image_url"),
                        image_s3_path=image_s3_path,
                        collected_at=datetime.utcnow(),
                    )

                    session.add(ad)
                    collected_count += 1

                    # Update progress
                    if collected_count % 10 == 0:
                        await _update_job_progress(session, job_id, collected_count)
                        await session.commit()

                except Exception as e:
                    logger.error(f"Error processing ad {ad_data.get('ad_id')}: {e}")
                    continue

            # Final commit
            await session.commit()

            # Update job status to completed
            await _update_job_status_db(
                session, job_id, "completed", collected_count=collected_count
            )

            logger.info(f"Collect task completed: {collected_count} ads collected")

        except Exception as e:
            logger.error(f"Error in collect task: {e}")
            await session.rollback()
            await _update_job_status_db(session, job_id, "failed", error=str(e))
            raise


async def _update_job_status_db(
    session: AsyncSession,
    job_id: str,
    status: str,
    collected_count: int = None,
    error: str = None,
):
    """Update job status in database."""
    result = await session.execute(
        select(CollectJob).where(CollectJob.job_id == UUID(job_id))
    )
    job = result.scalar_one_or_none()

    if job:
        job.status = status
        if collected_count is not None:
            job.collected_count = collected_count
        if error:
            job.error_message = error
        if status == "running":
            job.started_at = datetime.utcnow()
        if status in ("completed", "failed"):
            job.completed_at = datetime.utcnow()
        await session.commit()


async def _update_job_progress(session: AsyncSession, job_id: str, count: int):
    """Update job progress."""
    result = await session.execute(
        select(CollectJob).where(CollectJob.job_id == UUID(job_id))
    )
    job = result.scalar_one_or_none()
    if job:
        job.collected_count = count


async def _update_job_status(job_id: str, status: str, error: str = None):
    """Update job status (standalone)."""
    async with async_session() as session:
        await _update_job_status_db(session, job_id, status, error=error)
