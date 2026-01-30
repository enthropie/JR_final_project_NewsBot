import time
import json
import logging
import asyncio
from datetime import timedelta
from app.celery_app import celery_app
from app.config import settings
from app.news_parser import save_news_to_db
from app.redis_client import get_redis_client


NEWS_LATEST_KEY = 'news:latest'
NEWS_URL_SEEN_KEY = 'news:urls_seen'
NEWS_LATEST_IDS_KEY = 'news:latest_ids'
NEWS_LATEST_LIMIT = 100


logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.ping")
def ping():
    return True


@celery_app.task(name="app.tasks.scrape_news_and_save")
def scrape_news_and_save():
    return save_news_to_db()


@celery_app.task(name="app.tasks.make_post")
def make_post():
    return asyncio.run(make_post_service())