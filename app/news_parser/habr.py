import logging

import requests
from bs4 import BeautifulSoup

from app.news_parser.utils import normalize_published_at

HABR_BASE_URL = "https://habr.com/ru"
HABR_NEWS_URL = f"{HABR_BASE_URL}/news/"
HABR_ARTICLE_URL = f"{HABR_BASE_URL}/article/"

HABR_CARD_SELECTOR = "article.tm-articles-list__item"
HABR_TITLE_SELECTOR = "a"
HABR_TITLE_LINK_SELECTOR = "tm-title__link"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}

logger = logging.getLogger(__name__)


def parser_habr_list_html(html: str) -> list[dict]:
    """Метод извлекает требуемые части новости из html"""

    soup = BeautifulSoup(html, "html.parser")
    news_items: list[dict] = []

    article_tags = soup.select(HABR_CARD_SELECTOR)

    for article_tag in article_tags:
        title_link = article_tag.find(
            HABR_TITLE_SELECTOR,
            class_=HABR_TITLE_LINK_SELECTOR,
        )

        if title_link is None:
            continue

        title_text = title_link.get_text(strip=True)
        relative_url = title_link.get("href", "")

        if not relative_url:
            continue

        if relative_url.startswith("http"):
            full_url = relative_url
        else:
            full_url = f"https://habr.com{relative_url}"

        news_date_row = article_tag.find("time")
        news_date = (
            news_date_row.get("datetime", "")
            if news_date_row is not None
            else ""
        )

        text_row = article_tag.find("p")
        text = (
            text_row.get_text(strip=True)
            if text_row is not None
            else ""
        )

        news_item = {
            "title": title_text,
            "url": full_url,
            "source": "habr",
            "published_at": normalize_published_at(news_date),
            "text": text,
        }

        news_items.append(news_item)

    logger.info("Parsed %s Habr news items", len(news_items))
    return news_items


def fetch_habr_news_list(limit: int = 20) -> list[dict[str, str]]:
    """Получение коллекции сырых новостей"""

    try:
        response = requests.get(
            HABR_NEWS_URL,
            headers=DEFAULT_HEADERS,
            timeout=10,
        )
    except requests.RequestException as exc:
        logger.warning("Ошибка при парсинге Habr: %s", exc)
        return []

    if response.status_code != 200:
        logger.warning(
            "Habr returned non-200 status code: %s",
            response.status_code,
        )
        return []

    raw_items = parser_habr_list_html(response.text)
    return raw_items[:limit]


if __name__ == "__main__":
    news = fetch_habr_news_list()

    for news_item in news:
        logger.info(
            "News item:\n%s\n%s\n%s\n%s\n%s",
            news_item.get("title"),
            news_item.get("url"),
            news_item.get("published_at"),
            news_item.get("text"),
            news_item.get("source"),
        )
