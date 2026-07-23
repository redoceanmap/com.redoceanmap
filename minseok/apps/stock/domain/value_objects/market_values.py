from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Symbol:
    """분석 대상 종목 티커 (예: 'AAPL')."""

    code: str

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("Symbol code는 비어 있을 수 없습니다.")


@dataclass(frozen=True, slots=True)
class Price:
    """가격 (양수)."""

    value: float

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Price는 양수여야 합니다.")


@dataclass(frozen=True, slots=True)
class Quote:
    """현재가 + 전일 종가 — 등락률 산출용.

    previous_close는 벤더가 주지 못하면 None(등락률 미표시로 열화). 봉을 함께 받는
    차트와 달리 지수 스트립·헤더는 quote 하나로 등락률까지 내야 하므로 여기에 담는다.
    """

    price: Price
    previous_close: Price | None = None

    def change_pct(self) -> float | None:
        if self.previous_close is None:
            return None
        return self.price.value / self.previous_close.value - 1.0
