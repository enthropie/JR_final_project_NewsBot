import os
from telethon import TelegramClient
from dotenv import load_dotenv
from app.ai.google import take_last_post_and_rewrite
from app.utils import publish_post_to_db

async def send_message(message: str) -> str:
    """Отправка поста в Телеграмм канал"""

    load_dotenv()

    api_id = int(os.getenv("telegram_api_id"))
    api_hash = os.getenv("telegram_api_hash")
    channel_id = int(os.getenv("telegram_channel_id"))

    client = TelegramClient("session", api_id, api_hash)

    async with client:
        await client.send_message(channel_id, message)

    return "done"


async def make_post_service() -> bool:
    result = take_last_post_and_rewrite()
    if not result:
        return False

    news_id, text = result
    status_result = await send_message(text)
    publish_post_to_db(news_id, text)

    return bool(status_result)