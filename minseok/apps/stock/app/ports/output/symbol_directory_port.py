from __future__ import annotations

from abc import ABC, abstractmethod


class SymbolDirectoryPort(ABC):
    """티커 → 표시용 이름. 보드처럼 여러 종목을 한 화면에 늘어놓을 때만 쓴다."""

    @abstractmethod
    def display_name(self, ticker: str) -> str:
        """모르는 티커는 티커 자체를 돌려준다(빈 문자열·예외 금지)."""
        ...
