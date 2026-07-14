from __future__ import annotations

from pydantic import BaseModel


class StockAnalyzeResponse(BaseModel):
    """POST /stock/analyze 응답 — 기존 와이어 포맷(snake_case) 유지.

    필드 의미는 app DTO(StockAnalysis) 참고. 방향은 전망일 뿐 매매 추천이 아니다.
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
    atr_pct: float
    bb_percent_b: float
    volume_ratio: float
    obv_slope: float
    momentum_12_1: float
    reference_up_signal: bool
