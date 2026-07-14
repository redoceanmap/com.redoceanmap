from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UnlabeledNews:
    """특정 라벨러가 아직 라벨하지 않은 뉴스 — 라벨링 배치의 작업 단위."""

    news_id: int
    ticker: str
    title: str
