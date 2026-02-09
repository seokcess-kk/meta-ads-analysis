import asyncio
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.services.analyzer import analyzer
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Create async engine for task
engine = create_async_engine(settings.async_database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def run_async(coro):
    """Run async coroutine in sync context."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return loop.run_until_complete(coro)


@celery_app.task(bind=True, name="app.workers.analyze_task.analyze_image")
def analyze_image(self, ad_id: str):
    """
    Celery task to analyze ad image.

    Args:
        ad_id: Ad ID to analyze
    """
    logger.info(f"Starting image analysis for ad: {ad_id}")

    try:
        run_async(_analyze_image_async(ad_id))
        logger.info(f"Image analysis completed for ad: {ad_id}")
    except Exception as e:
        logger.error(f"Image analysis failed for ad {ad_id}: {e}")
        raise


async def _analyze_image_async(ad_id: str):
    """Async implementation of image analysis."""
    async with async_session() as session:
        await analyzer.analyze_image(session, ad_id)


@celery_app.task(bind=True, name="app.workers.analyze_task.analyze_copy")
def analyze_copy(self, ad_id: str):
    """
    Celery task to analyze ad copy.

    Args:
        ad_id: Ad ID to analyze
    """
    logger.info(f"Starting copy analysis for ad: {ad_id}")

    try:
        run_async(_analyze_copy_async(ad_id))
        logger.info(f"Copy analysis completed for ad: {ad_id}")
    except Exception as e:
        logger.error(f"Copy analysis failed for ad {ad_id}: {e}")
        raise


async def _analyze_copy_async(ad_id: str):
    """Async implementation of copy analysis."""
    async with async_session() as session:
        await analyzer.analyze_copy(session, ad_id)


@celery_app.task(bind=True, name="app.workers.analyze_task.analyze_batch")
def analyze_batch(self, ad_ids: List[str], types: List[str] = None):
    """
    Celery task to analyze multiple ads.

    Args:
        ad_ids: List of ad IDs to analyze
        types: List of analysis types ("image", "copy")
    """
    types = types or ["image", "copy"]
    logger.info(f"Starting batch analysis for {len(ad_ids)} ads")

    try:
        run_async(_analyze_batch_async(ad_ids, types))
        logger.info(f"Batch analysis completed for {len(ad_ids)} ads")
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise


async def _analyze_batch_async(ad_ids: List[str], types: List[str]):
    """Async implementation of batch analysis."""
    async with async_session() as session:
        for ad_id in ad_ids:
            try:
                if "image" in types:
                    await analyzer.analyze_image(session, ad_id)
                if "copy" in types:
                    await analyzer.analyze_copy(session, ad_id)
            except Exception as e:
                logger.error(f"Error analyzing ad {ad_id}: {e}")
                continue
