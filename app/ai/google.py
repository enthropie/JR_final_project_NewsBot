import logging
import os
from typing import Optional, Tuple

from dotenv import load_dotenv
from google import genai
from PIL import Image
from sqlalchemy import select

from app.database import SessionLocal
from app.models import NewsItem

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")


def generate_image(text: str) -> str:
    """
    Метод для генерации изображения для новости Телеграмма по ее тексту
    """
    client = genai.Client()

    prompt = f"Generate image for social network for news: {text}"
    logger.info("Generating image for news")

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
    )

    for part in response.parts:
        if part.text is not None:
            logger.debug("Model text response: %s", part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            image.save("generated_image.png")
            logger.info("Image saved as generated_image.png")

    return "generated_image.png"


def rewrite_news(text: str) -> str:
    """
    Метод переформулирует оригинальную новость при помощи нейросети от google
    """

    client = genai.Client()

    prompt = f"""
Ты редактор новостей.

Перепиши новость для Telegram:
— коротко
— живо
— 1–2 абзаца
— без клише
- без разметки markdown

Текст:
{text}
"""

    logger.info("Rewriting news text")

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    logger.debug("Original text: %s", text)
    logger.debug("Model response: %s", response)

    return response.text.strip()


def take_last_post_and_rewrite(
    limit: int = 1,
) -> Optional[Tuple[int, str]]:

    """
    Берем из БД новость, которая не отправлась как пост ранее (status == NULL)
    и является тематически релевантной нашему каналу is_relevant == True,
    переписываем ее при помощи нейросети и формируем текст для поста в Телеграмм.
    """

    session = SessionLocal()

    try:
        logger.info("Fetching last relevant news item")

        stmt = (
            select(NewsItem)
            .where(
                NewsItem.is_relevant.is_(True),
                NewsItem.status.is_(None),
            )
            .limit(limit)
        )

        news_item = session.scalars(stmt).first()

        if not news_item:
            logger.info("No relevant news items found")
            return None

        logger.info(
            "Rewriting news item id=%s title=%s",
            news_item.id,
            news_item.title,
        )

        rewritten_text = rewrite_news(
            f"{news_item.title}\n\n{news_item.summary}"
        )

        return news_item.id, rewritten_text

    except Exception:
        logger.exception("Error while rewriting last news item")
        return None

    finally:
        session.close()
