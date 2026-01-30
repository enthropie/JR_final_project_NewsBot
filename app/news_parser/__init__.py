import hashlib
import logging
from typing import Any, Mapping

from app.database import SessionLocal
from app.models import NewsItem
from app.news_parser import cnews, habr
from app.news_parser.utils import is_relevant, normalize_published_at

logger = logging.getLogger(__name__)

SOURCE = (
    ("habr", habr.fetch_habr_news_list),
    ("cnews", cnews.fetch_cnews_news_list),
)


def make_news_id(source: str, url: str) -> str:
    base = f"{source}:{url}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def generate_news_id(source: str, url: str) -> str:
    """habr:https://habr.com/ru/news/qazxsw123/"""
    base = f"{source}:{url}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def normalize_raw_news(
    source_name: str,
    raw_item: Mapping[str, Any],
) -> NewsItem:
    # ---------- title ----------
    raw_title = raw_item.get("title", "")
    title = str(raw_title).strip()

    # ---------- url ----------
    raw_url = raw_item.get("url") or raw_item.get("link")
    if not raw_url:
        raise ValueError("Не смогли нормализовать url")

    url = str(raw_url).strip()

    # ---------- id ----------
    hash_id = make_news_id(source_name, url)

    # ---------- summary ----------
    raw_summary = raw_item.get("text") or raw_item.get("summary") or ""
    summary = str(raw_summary).strip()

    # ---------- source ----------
    raw_source = raw_item.get("source") or source_name
    source = str(raw_source).strip()

    # ---------- published_at ----------
    raw_published_at = (
        raw_item.get("datetime") or raw_item.get("published_at")
    )
    published_at_dt = normalize_published_at(raw_published_at)

    # ---------- keywords ----------
    keywords = ""

    news_item = NewsItem(
        id=hash_id,
        title=title,
        url=url,
        summary=summary,
        source=source,
        published_at=published_at_dt,
        keywords=keywords,
        is_relevant=is_relevant(title, summary),
    )

    logger.debug(
        "Normalized news item: source=%s url=%s",
        source_name,
        url,
    )

    return news_item


def collect_from_all_source() -> list[NewsItem]:
    """Парсинг всех источников"""

    collected_news: list[NewsItem] = []

    for source_name, fetch_func in SOURCE:
        logger.info("Fetching news from source: %s", source_name)

        try:
            raw_items = fetch_func()
        except Exception:
            logger.exception(
                "Ошибка при парсинге новостей из источника %s",
                source_name,
            )
            continue

        for raw_item in raw_items:
            try:
                news_item = normalize_raw_news(
                    source_name=source_name,
                    raw_item=raw_item,
                )
            except Exception:
                logger.exception(
                    "Ошибка при нормализации новости из %s",
                    source_name,
                )
                continue

            collected_news.append(news_item)

    logger.info("Collected %s news items", len(collected_news))
    return collected_news


def save_news_to_db() -> int:
    """Метод сохранения NewsItems-ов в БД"""

    db = SessionLocal()
    saved = 0

    items = collect_from_all_source()
    logger.info("Saving %s news items to database", len(items))

    for item in items:
        try:
            db.add(item)
            db.commit()
            saved += 1
            logger.debug("Saved news item id=%s", item.id)
        except Exception:
            db.rollback()
            # новость уже есть — пропускаем
            logger.debug(
                "News item already exists or failed to save: id=%s",
                item.id,
            )
            continue

    db.close()
    logger.info("Saved %s new news items", saved)
    return saved


if __name__ == "__main__":
    all_news = collect_from_all_source()
    logger.info("Collected news: %s", all_news)
