from celery import Celery
from app.config import settings
from datetime import timedelta

celery_app = Celery(
    "newsbot",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    broker_connection_retry_on_startup=True,
    result_expires=3600,
    task_default_queue="newsbot",
)



celery_app.conf.beat_schedule = {
    "scrape-news-every-hour": {
        "task": "app.tasks.scrape_news_and_save",
        "schedule": timedelta(hours=1),
    },
    "make-post-every-20-min": {
        "task": "app.tasks.make_post",
        "schedule": timedelta(minutes=20),
    },
}


celery_app.autodiscover_tasks(["app"])
