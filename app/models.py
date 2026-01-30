import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from app.database import Base


class NewsItem(Base):
    __tablename__ = "news"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    title = Column(String, nullable=False)
    url = Column(String, nullable=True)

    summary = Column(Text, nullable=False)

    source = Column(String, nullable=False)

    published_at = Column(DateTime, nullable=True)

    keywords = Column(String, nullable=True)

    is_relevant = Column(Boolean, nullable=True)

    status = Column(String, nullable=True)


class Post(Base):
    __tablename__ = "posts"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    news_id = Column(
        String,
        ForeignKey("news.id", ondelete="CASCADE"),
        nullable=False,
    )

    generated_text = Column(Text, nullable=False)

    published_at = Column(DateTime, nullable=True)

    status = Column(
        String,
        default="published",
        nullable=False,
    )  # new / generated / published / failed

