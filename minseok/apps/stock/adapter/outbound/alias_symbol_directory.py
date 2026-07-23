"""티커 → 표시용 한글명.

`symbol_resolver`가 이미 들고 있는 한국어명 → 티커 별칭 사전을 뒤집어 재사용한다
(같은 표기를 두 곳에서 관리하지 않기 위해서다). 별칭에 없는 티커는 티커 그대로 쓴다 —
보드는 이름이 없어도 동작해야 하므로 네트워크 조회(KRX 목록)는 하지 않는다.
"""
from __future__ import annotations

from stock.adapter.outbound.symbol_resolver import _OVERSEAS_ALIASES
from stock.app.ports.output.symbol_directory_port import SymbolDirectoryPort

# 워치리스트 한국 종목 — 2개 고정(2026-07-21 확정)이라 별칭 사전 대신 여기 직접 둔다
_KR_NAMES = {"005930": "삼성전자", "000660": "SK하이닉스"}


def _build_reverse() -> dict[str, str]:
    # 한 티커에 별칭이 여럿이면(구글/알파벳 → GOOGL) 사전에 먼저 나온 표기를 대표로 쓴다
    reverse: dict[str, str] = {}
    for name, ticker in _OVERSEAS_ALIASES.items():
        reverse.setdefault(ticker, name)
    return reverse


_REVERSE = _build_reverse()


class AliasSymbolDirectory(SymbolDirectoryPort):

    def display_name(self, ticker: str) -> str:
        base = ticker.split(".")[0]  # 005930.KS → 005930
        return _KR_NAMES.get(base) or _REVERSE.get(base.upper()) or ticker
