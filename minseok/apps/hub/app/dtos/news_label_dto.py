"""뉴스 라벨 수집 계약 DTO.

허브(hub)가 공개하는 자동화 협력 계약의 일부. 라벨링 배치(scripts/label_news.py)가
미라벨 뉴스를 받아 LLM 라벨을 되돌려주면 NewsLabelStoragePort로 스포크(stock)에
저장을 위임한다. 원시 값만 담는 순수 객체다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NewsLabelItem:
    news_id: int
    labeler: str  # 라벨러 버전(예: exaone-2.4b-awq) — 재라벨링 공존 키
    sentiment: float  # -1.0(악재) ~ +1.0(호재)
    event_type: str
    confidence: float  # 0.0 ~ 1.0


@dataclass(frozen=True)
class UnlabeledNewsItem:
    news_id: int
    ticker: str
    title: str
