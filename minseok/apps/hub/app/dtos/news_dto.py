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
    published_at: datetime | None = None
