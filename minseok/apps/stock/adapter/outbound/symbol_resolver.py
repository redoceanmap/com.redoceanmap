"""자유 질의(종목명·티커) → 종목 코드 해석.

한국 종목명은 KRX 상장 목록(FinanceDataReader)으로 6자리 코드에 매핑하고,
그 외는 야후 검색으로 보조한다. 해외 종목의 한국어 이름(예: "테슬라")은
소비자(chat)의 LLM이 티커로 정규화해 넘기는 것을 전제로 한다.
"""
from __future__ import annotations

import asyncio
import logging
import re

import FinanceDataReader as fdr
import yfinance as yf

from stock.app.exceptions import MarketDataUnavailableError

logger = logging.getLogger(__name__)

_KR_CODE_RE = re.compile(r"^\d{6}$")
_US_TICKER_RE = re.compile(r"^[A-Za-z][A-Za-z.\-]{0,5}$")

_krx_names: dict[str, str] | None = None  # 종목명 → 6자리 코드 (프로세스 캐시)


def _load_krx_names() -> dict[str, str]:
    global _krx_names
    if _krx_names is None:
        listing = fdr.StockListing("KRX")
        _krx_names = {
            str(row.Name).strip(): str(row.Code)
            for row in listing.itertuples()
            if str(row.Market).startswith(("KOSPI", "KOSDAQ"))
        }
        logger.info("[symbol-resolver] KRX 상장 목록 캐시: %d종목", len(_krx_names))
    return _krx_names


def _resolve_sync(query: str) -> str:
    q = query.strip()
    if _KR_CODE_RE.match(q):
        return q
    if _US_TICKER_RE.match(q):
        return q.upper()

    names = _load_krx_names()
    if q in names:
        return names[q]
    compact = q.replace(" ", "")
    if compact in names:
        return names[compact]

    # 부분 일치: "하이닉스" → "SK하이닉스". 유일할 때만 채택, 여러 개면 후보를 알려준다.
    if len(compact) >= 2:
        partial = [name for name in names if compact in name]
        if len(partial) == 1:
            return names[partial[0]]
        if 2 <= len(partial) <= 5:
            raise MarketDataUnavailableError(
                f"'{query}'에 해당하는 종목이 여러 개입니다: {', '.join(sorted(partial))}"
            )

    # 마지막 보조: 야후 검색 (영어 회사명 등).
    # 한글 질의는 제외 — KRX에 없는 한글 이름이 무관한 해외 티커에 오매칭되는 것을 막는다.
    if not _has_hangul(q):
        try:
            quotes = yf.Search(q, max_results=5).quotes
        except Exception:
            quotes = []
        for item in quotes:
            if item.get("quoteType") == "EQUITY" and item.get("symbol"):
                return str(item["symbol"])

    raise MarketDataUnavailableError(f"종목을 찾지 못했습니다: {query}")


def _has_hangul(text: str) -> bool:
    return any("가" <= ch <= "힣" for ch in text)


async def resolve_symbol(query: str) -> str:
    """질의를 종목 코드(한국 6자리 또는 해외 티커)로 해석한다. 동기 I/O는 스레드 분리."""
    return await asyncio.to_thread(_resolve_sync, query)
