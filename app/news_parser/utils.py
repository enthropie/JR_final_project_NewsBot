from datetime import datetime
from typing import Any, Mapping

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def normalize_published_at(raw_value: Any) -> datetime | None:
    if isinstance(raw_value, datetime):
        return raw_value

    if raw_value is None or raw_value == "":
        return None

    if isinstance(raw_value, str):
        possible_formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%d.%m-%Y, %H:%M",
        ]
        for possible_format in possible_formats:
            try:
                return datetime.strptime(raw_value, possible_format)
            except ValueError:
                continue
        return None
    return None


def is_relevant(title: str, summary: str) -> bool:
    """Вычисление, является ли новость релевантной тематике нашего канала"""

    model = get_model()

    SIMILARITY_THRESHOLD = 0.35

    KEYWORDS = {
        "python",
        "ai", "artificial intelligence",
        "machine learning", "ml",
        "data science", "datascience",
        "deep learning",
    }

    TOPIC_TEXT = """
    Python programming, artificial intelligence, machine learning,
    deep learning, data science, neural networks
    """
    TOPIC_EMBEDDING = model.encode(TOPIC_TEXT)



    text = f"{title} {summary}".lower()

    # Keyword check
    if any(keyword in text for keyword in KEYWORDS):
        return True

    # Vector similarity check
    text_embedding = model.encode(text)
    similarity = cosine_similarity(
        [text_embedding],
        [TOPIC_EMBEDDING]
    )[0][0]

    return similarity >= SIMILARITY_THRESHOLD
