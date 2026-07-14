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
    atr_pct: float = 0.0              # 변동성 비율 (ATR14/종가)
    bb_percent_b: float = 0.5         # 볼린저 %B (0=하단, 1=상단)
    volume_ratio: float = 1.0         # 최근 5일 평균 거래량 / 20일 평균
    obv_slope: float = 0.0            # OBV 20일 정규화 기울기 (수급 방향)
    momentum_12_1: float = 0.0        # 12-1 모멘텀 (이력 부족 시 0.0)
    reference_up_signal: bool = False  # 백테스트 검증(인샘플+홀드아웃) 통과한 RSI+BB ±0.35 UP 참고 신호 — 확률 아님
