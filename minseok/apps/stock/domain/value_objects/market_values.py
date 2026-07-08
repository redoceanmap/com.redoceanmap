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
