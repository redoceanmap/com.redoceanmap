from __future__ import annotations

import asyncio
import logging
from typing import Any

import yfinance as yf

from stock.app.exceptions import MarketDataUnavailableError
from stock.app.ports.output.market_data_port import MarketDataPort
from stock.domain.services.indicator_calculator import IndicatorCalculator
from stock.domain.value_objects.indicators import Indicators
from stock.domain.value_objects.market_values import Price, Symbol

logger = logging.getLogger(__name__)

HISTORY_PERIOD = "6mo"
MAX_HEADLINES = 5


def yahoo_candidates(code: str) -> list[str]:
    """야후 티커 후보. 한국 6자리 숫자 코드는 코스피(.KS) → 코스닥(.KQ) 순으로 시도."""
    if code.isdigit() and len(code) == 6:
        return [f"{code}.KS", f"{code}.KQ"]
    return [code.upper()]


class YFinanceMarketDataAdapter(MarketDataPort):
    """야후 파이낸스(yfinance)로 시세·지표·뉴스를 조회한다.

    키 발급 없이 한국(코스피/코스닥, 지연 시세)·미국 종목을 커버한다. 지연 시세로
    충분한 방향 전망 분석용이며, 실시간이 필요해지면 KIS 등 벤더 어댑터로 교체한다
    (MarketDataPort 계약 동일). yfinance는 동기 라이브러리라 asyncio.to_thread로
    이벤트 루프에서 분리한다. 지표 계산은 도메인 서비스(IndicatorCalculator)에 위임.
    """

    def __init__(self) -> None:
        self._calculator = IndicatorCalculator()
        # 한 요청(analyze) 안에서 latest_price/indicators가 이력을 공유하도록 캐시.
        # 프로바이더가 요청마다 어댑터를 새로 만들므로 요청 범위를 넘지 않는다.
        self._history_cache: dict[str, tuple[str, Any]] = {}

    async def latest_price(self, symbol: Symbol) -> Price:
        _, history = await self._history(symbol)
        return Price(value=float(history["Close"].iloc[-1]))

    async def indicators(self, symbol: Symbol) -> Indicators:
        _, history = await self._history(symbol)
        try:
            return self._calculator.compute(
                closes=[float(v) for v in history["Close"]],
                lows=[float(v) for v in history["Low"]],
                highs=[float(v) for v in history["High"]],
            )
        except ValueError as e:
            raise MarketDataUnavailableError(f"{symbol.code}: {e}")

    async def recent_headlines(self, symbol: Symbol) -> list[str]:
        ticker, _ = await self._history(symbol)
        try:
            return await asyncio.to_thread(self._fetch_news, ticker)
        except Exception:
            # 뉴스는 보조 신호 — 실패해도 분석 자체는 지표만으로 진행한다.
            logger.warning("[yfinance] 뉴스 조회 실패: %s", ticker, exc_info=True)
            return []

    async def _history(self, symbol: Symbol) -> tuple[str, Any]:
        if symbol.code not in self._history_cache:
            self._history_cache[symbol.code] = await asyncio.to_thread(
                self._fetch_history, symbol.code
            )
        return self._history_cache[symbol.code]

    def _fetch_history(self, code: str) -> tuple[str, Any]:
        for ticker in yahoo_candidates(code):
            history = yf.Ticker(ticker).history(period=HISTORY_PERIOD, auto_adjust=True)
            if not history.empty:
                logger.info("[yfinance] %s → %s (%d행)", code, ticker, len(history))
                return ticker, history
        raise MarketDataUnavailableError(f"시세 데이터를 찾지 못했습니다: {code}")

    @staticmethod
    def _fetch_news(ticker: str) -> list[str]:
        titles: list[str] = []
        for item in yf.Ticker(ticker).news or []:
            # yfinance 뉴스 스키마: 신버전 {"content": {"title": ...}} / 구버전 {"title": ...}
            title = (item.get("content") or {}).get("title") or item.get("title")
            if title:
                titles.append(title)
        return titles[:MAX_HEADLINES]
