from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    debug: bool = False
    redis_url: str = 'redis://127.0.0.1:6379/0'
    DATABASE_URL: str = 'sqlite:///news.db'

    telegram_api_id: int = 0
    telegram_api_hash: str = ''
    telegram_channel_id: str = ''

    GEMINI_API_KEY: str = ''

    @property
    def keywords_list(self) -> list[str]:
        raw_value = self.news_keywords
        parts = [part.strip() for part in raw_value.split(',') if part.strip()]
        return parts


settings = Settings()


if __name__ == '__main__':
    print(settings.telegram_api_id)
    print(settings.telegram_api_hash)
    print(settings.telegram_channel_id)
    print(settings.keywords_list)