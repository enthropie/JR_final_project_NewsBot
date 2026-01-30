import logging
from datetime import datetime

from app.database import SessionLocal
from app.models import NewsItem, Post

logger = logging.getLogger(__name__)


def publish_post_to_db(news_id: int, text: str) -> None:
    """Сохранение поста, отправленного в Telegram-канал, в БД."""
    session = SessionLocal()

    try:
        logger.info("Publishing post to DB for news_id=%s", news_id)

        news = session.get(NewsItem, news_id)
        if not news:
            logger.error("NewsItem not found: news_id=%s", news_id)
            raise ValueError("NewsItem not found")

        # обновляем статус новости
        news.status = "Processed"
        logger.debug("Updated news status to Processed for news_id=%s", news_id)

        # сохраняем пост
        post = Post(
            news_id=news_id,
            generated_text=text,
            published_at=datetime.utcnow(),
            status="published",
        )

        session.add(post)
        session.commit()

        logger.info("Post successfully saved for news_id=%s", news_id)

    except Exception:
        session.rollback()
        logger.exception(
            "Error while publishing post to DB for news_id=%s",
            news_id,
        )
        raise

    finally:
        session.close()
        logger.debug("DB session closed for news_id=%s", news_id)
