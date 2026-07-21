from __future__ import annotations

from pydantic import BaseModel


class SignalContributionSchema(BaseModel):
    key: str            # sentiment | rsi | trend | bollinger | obv | momentum
    signal: float       # -1 ~ 1 원신호
    weight: float
    contribution: float  # signal × weight


class InsightSchema(BaseModel):
    key: str
    tone: str  # positive | neutral | warning
    text: str


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
    score: float                       # 가중 합산 종합 점수 (-1~1)
    up_threshold: float                # 방향 판정 기준 — 게이지 눈금용
    down_threshold: float
    neutral_reason: str | None         # atr_veto | volume_confirm | null
    signals: list[SignalContributionSchema]
    insights: list[InsightSchema]
