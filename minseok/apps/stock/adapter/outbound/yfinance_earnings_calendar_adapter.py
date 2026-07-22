from __future__ import annotations

import asyncio
import logging
from datetime import UTC, date, datetime

import yfinance as yf

from stock.adapter.outbound.yfinance_market_data_adapter import yahoo_candidates
from stock.app.ports.output.earnings_calendar_port import EarningsCalendarPort

logger = logging.getLogger(__name__)

EARNINGS_LIMIT = 20  # 과거 ~12분기 + 예정 — yfinance 제공 범위 상한 여유

# 심볼당 일 1회 캐시(모듈 전역) — capture가 하루 68종목을 돌아도 벤더 호출은 종목당 1회.
# 실패(429 포함)도 그날은 빈 리스트로 캐시해 재타격을 막는다(무-veto 열화).
_CACHE: dict[str, tuple[str, list[date]]] = {}


class YFinanceEarningsCalendarAdapter(EarningsCalendarPort):
    """yfinance Ticker.get_earnings_dates 래퍼 — 과거+예정 발표일을 date 리스트로."""

    async def earnings_dates(self, symbol: str) -> list[date]:
        code = symbol.strip().upper()
        today = datetime.now(UTC).date().isoformat()
        cached = _CACHE.get(code)
        if cached is not None and cached[0] == today:
            return cached[1]
        dates = await asyncio.to_thread(self._fetch, code)
        _CACHE[code] = (today, dates)
        return dates

    @staticmethod
    def _fetch(code: str) -> list[date]:
        for ticker in yahoo_candidates(code):
            try:
                df = yf.Ticker(ticker).get_earnings_dates(limit=EARNINGS_LIMIT)
                if df is None or df.empty:
                    continue
                return sorted({ts.date() for ts in df.index if ts is not None})
            except Exception as e:  # 벤더 오류(429 등)는 무-veto 열화 — 예측을 막지 않는다
                logger.warning("[earnings] %s 발표일 조회 실패: %s", ticker, e)
                return []
        return []
