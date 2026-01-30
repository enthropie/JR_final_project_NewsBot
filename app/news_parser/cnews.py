import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

CNEWS_NEWS_URL = "https://www.cnews.ru/news"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}

logger = logging.getLogger(__name__)


def parse_cnews_article(url: str) -> str:
    """Метод забирает полный текст новости с сайта cnews, открывая для этого ссылку"""

    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=(5, 15),
        )
        response.raise_for_status()
    except requests.Timeout:
        logger.warning("CNews timeout: %s", url)
        return ""
    except requests.RequestException as exc:
        logger.warning("CNews error %s: %s", url, exc)
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    article = soup.select_one("article.news_container")
    paragraphs: list[str] = []

    if article:
        for paragraph in article.find_all("p", recursive=False):
            text = paragraph.get_text(strip=True)
            if text:
                paragraphs.append(text)

    summary = "\n".join(paragraphs)
    logger.debug("Parsed article summary length=%s url=%s", len(summary), url)

    return summary


def parse_cnews_list_html(html: str) -> list[dict]:
    """Метод извлекает требуемые части новости из html"""

    soup = BeautifulSoup(html, "html.parser")
    news_items: list[dict] = []

    items = soup.select("div.allnews_item")

    for item in items:
        link = item.select_one("a.ani-postname")
        if not link:
            continue

        title = link.get_text(strip=True)
        url = link.get("href")

        time_tag = item.select_one(".ani-date time:last-child")
        time_text = time_tag.get_text(strip=True) if time_tag else "00:00"

        published_at = None
        date_match = re.search(r"/(\d{4}-\d{2}-\d{2})_", url or "")
        if date_match:
            published_at = datetime.fromisoformat(
                f"{date_match.group(1)} {time_text}"
            )

        summary = parse_cnews_article(url)

        news_items.append(
            {
                "title": title,
                "url": url,
                "source": "cnews",
                "summary": summary,
                "published_at": published_at,
            }
        )

    logger.info("Parsed %s news items from CNews", len(news_items))
    return news_items


def fetch_cnews_news_list(limit: int = 20) -> list[dict]:
    """Получение коллекции сырых новостей"""

    logger.info("Fetching CNews news list")

    try:
        response = requests.get(
            CNEWS_NEWS_URL,
            headers=DEFAULT_HEADERS,
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("CNews parser error: %s", exc)
        return []

    items = parse_cnews_list_html(response.text)
    return items[:limit]


if __name__ == "__main__":
    news = fetch_cnews_news_list()
    for item in news:
        logger.info("News item: %s", item)
