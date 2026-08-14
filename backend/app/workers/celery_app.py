"""
Celery application configuration.

Uses Redis as both broker (task queue) and result backend.
Tasks are auto-discovered from app.workers.tasks.

Design decision: Celery was chosen over simpler alternatives (BackgroundTasks,
threading) because:
1. It is an industry-standard async task queue.
2. Tasks survive server restarts (persisted in Redis).
3. Independent scaling — workers can run on separate machines.
4. Built-in retry logic for failed tasks.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "complaint_tracker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # Re-deliver tasks if a worker crashes mid-execution
    worker_prefetch_multiplier=1,  # Fair scheduling across workers
)

# Auto-discover tasks in the workers package
celery_app.autodiscover_tasks(["app.workers"])
