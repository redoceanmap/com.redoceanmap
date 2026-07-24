"""주식 분석 계약 DTO.

허브(hub)가 공개하는 앱 간 협력 계약의 일부. stock(스포크)이 채워서 반환하고
chat(스포크)이 서술 생성에 소비한다. 원시 수치만 담으며(문장화는 소비자 관심사),
외부 의존 없는 순수 객체다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StockAnalysisResult:
    symbol: str            # 해석된 종목 코드 (예: '005930', 'AAPL')
    price: float
    direction: str         # UP | DOWN | NEUTRAL
    confidence: float      # 0.0 ~ 1.0
    sentiment: float       # -1.0 ~ 1.0
    sentiment_label: str   # 긍정 | 중립 | 부정
    rsi: float
    ma20: float
    ma50: float
    support: float
    resistance: float
    headlines: list[str]
    atr_pct: float = 0.0               # ATR(14)/종가 — 일 변동성 비율
    bb_percent_b: float = 0.5          # 볼린저 %B (0=하단, 1=상단)
    volume_ratio: float = 1.0          # 최근 5일 평균 거래량 / 20일 평균
    obv_slope: float = 0.0             # OBV 20일 정규화 기울기 (수급 방향)
    momentum_12_1: float = 0.0         # 12-1 모멘텀 (이력 부족 시 0.0)
    reference_up_signal: bool = False  # 백테스트 검증 통과 RSI+BB ±0.35 UP 참고 신호 — 확률 아님
    score: float = 0.0                 # 가중 합산 종합 점수 (-1~1) — 신호 세기(약/보통/강) 판정용
    up_threshold: float = 0.3          # 방향 판정 기준 (프론트 strength()와 동일 공식)
    down_threshold: float = -0.3
