from pydantic import BaseModel, Field, AnyHttpUrl
from datetime import datetime
from uuid import UUID


class NewsItem(BaseModel):
    id: str = Field(
        ...,
        description="ID news item.",
        examples=['fhyy5fhg443asdgfhqwe']
    )
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Title of the news item.",
        examples=['Django 6.0 released', 'Вышла новая версия Python 3.14']
    )
    # url: AnyHttpUrl = Field(
    url: str = Field(
        ...,
        description="URL original arcticle.",
        examples=['http://habr.com/news/python/1234']
    )
    summary: str = Field(
        default=None,
        description="Summary of the news item.",
        examples=['Краткий обзор Django 6.0 и его ключевые отличия']
    )
    source: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Source of the news item.",
        examples=['habr', 'rbc']
    )
    published_at: datetime | None = Field(
        ...,
        description="Original date published the news.",
        examples=['2025-12-16T20:30:00Z']
    )
    keywords: str = Field(
        default = None,
        description="Keywords of the news item.",
        examples=['python, django, fastapi']
    )


class Keyword(BaseModel):
    id: int = Field(
        ...,
        description='Keyword id.',
        examples=[1, 2, 3]
    )
    word: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Keyword word.",
        examples=['python', 'django']
    )

