"""뉴스 수집 계약 DTO.

허브(hub)가 공개하는 자동화(n8n) 협력 계약의 일부. 허브 인바운드 라우터가 받아
NewsStoragePort로 스포크(stock)에 저장을 위임한다. 원시 값만 담는 순수 객체다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewsItem:
    title: str
    source: str
    url: str
    ticker: str = ""  # 관련 종목 티커(예: 005930.KS, NVDA) — 학습 라벨 조인 키
    published_at: datetime | None = None


@dataclass(frozen=True)
class NewsHit:
    """의미 검색(NewsSearchPort) 히트 1건 — 뉴스 + LLM 라벨(있으면)."""

    title: str
    ticker: str                     # 종목 무관 기사면 ""
    published_at: datetime | None
    sentiment: float | None = None  # -1.0(악재) ~ +1.0(호재), 라벨 없으면 None
    event_type: str | None = None
    source: str = ""
