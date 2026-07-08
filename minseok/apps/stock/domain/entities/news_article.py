from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class NewsArticle:
    """수집된 금융 뉴스 1건. url이 자연 유니크 키(중복 수집 방지)."""

    title: str
    source: str
    url: str
    published_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.title or not self.url:
            raise ValueError("NewsArticle은 title과 url이 필수입니다.")
