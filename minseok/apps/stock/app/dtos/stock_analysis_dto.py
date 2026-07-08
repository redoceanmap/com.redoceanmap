from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StockAnalysis:
    """analyze 1회 결과 — 라우터/외부로 나가는 평면 DTO.

    구조화된 분석 데이터만 담는다(최종 서술은 소비자 몫). 방향은 전망일 뿐 매매 추천이 아니다.
    """

    symbol: str
    price: float
    direction: str          # UP / DOWN / NEUTRAL
    confidence: float
    sentiment: float
    sentiment_label: str
    rsi: float
    ma20: float
    ma50: float
    support: float
    resistance: float
    headlines: list[str]
