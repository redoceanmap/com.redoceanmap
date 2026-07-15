"""상권 뉴스 수집·검색 계약 DTO.

허브(hub)가 공개하는 앱 간 협력 계약의 일부. 수집 배치가 허브 인바운드 라우터로 넣고
market(스포크)이 저장·임베딩·검색을 구현, chat(스포크)이 상권 답변 근거로 소비한다.
주식 뉴스(news_dto)와 별개 코퍼스 — 종목이 아니라 지역 어간(area_tag)이 조인 키다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MarketNewsItem:
    title: str
    source: str
    url: str
    area_tag: str = ""  # 지역 어간(예: 성수, 홍대) — 정책·시황 공통 기사는 ""
    published_at: datetime | None = None


@dataclass(frozen=True)
class MarketNewsHit:
    """의미 검색(MarketNewsSearchPort) 히트 1건."""

    title: str
    area_tag: str
    published_at: datetime | None
    source: str = ""
