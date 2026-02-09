from celery import Celery

from app.config import settings

celery_app = Celery(
    "meta_ads_worker",
    broker=settings.celery_broker_url,
    backend=settings.redis_url,
    include=[
        "app.workers.collect_task",
        "app.workers.analyze_task",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    result_expires=86400,  # Results expire after 1 day
)

# Task routes
celery_app.conf.task_routes = {
    "app.workers.collect_task.*": {"queue": "collect"},
    "app.workers.analyze_task.*": {"queue": "analyze"},
}
