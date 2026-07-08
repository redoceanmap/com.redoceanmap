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
