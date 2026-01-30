import logging
from fastapi import APIRouter, status
from app.news_parser import collect_from_all_source, save_news_to_db
from app.redis_client import ping_redis
from app.schemas import NewsItem
from app.tasks import ping
from app.telegram.publisher import make_post_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health/")
async def health_check():
    redis_ok = ping_redis()

    try:
        ping.delay()
        celery_ok = True
    except Exception:
        celery_ok = False

    return {
        "fastapi": "ok",
        "redis": redis_ok,
        "celery": celery_ok,
    }



@router.get(
    "/news/scrape/",
    response_model=list[NewsItem],
    status_code=status.HTTP_200_OK,
)
async def scrape_news():
    logger.info("Scraping news without saving")

    news_items = collect_from_all_source()

    logger.info("Scraped %s news items", len(news_items))
    return news_items


@router.get(
    "/news/scrape_and_save/",
    response_model=int,
    status_code=status.HTTP_200_OK,
)
async def scrape_news_and_save():
    logger.info("Scraping news and saving to database")

    saved_count = save_news_to_db()

    logger.info("Saved %s news items to database", saved_count)
    return saved_count


@router.post("/telegram/post", status_code=status.HTTP_200_OK)
async def make_post():
    logger.info("Creating Telegram post")
    return await make_post_service()
