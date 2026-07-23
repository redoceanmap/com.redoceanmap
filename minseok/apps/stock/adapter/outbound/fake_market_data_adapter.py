from __future__ import annotations

from datetime import UTC, datetime, timedelta

from stock.app.ports.output.market_data_port import MarketDataPort
from stock.domain.entities.price_bar import PriceBar
from stock.domain.value_objects.indicators import Indicators
from stock.domain.value_objects.market_values import Price, Quote, Symbol


class FakeMarketDataAdapter(MarketDataPort):
    """실데이터(미국 주식 벤더) 연동 전 임시 가짜 시세/지표/뉴스. 고정값을 반환한다."""

    async def latest_price(self, symbol: Symbol) -> Price:
        return Price(value=225.0)

    async def quote(self, symbol: Symbol) -> Quote:
        return Quote(price=Price(value=226.5), previous_close=Price(value=224.0))

    async def indicators(self, symbol: Symbol) -> Indicators:
        return Indicators(rsi=58.0, ma20=222.0, ma50=210.0, support=205.0, resistance=235.0)

    async def daily_bars(self, symbol: Symbol) -> list[PriceBar]:
        start = datetime(2024, 1, 1, tzinfo=UTC)
        return [
            PriceBar(
                ticker=symbol.code, timeframe="1d", ts=start + timedelta(days=i),
                open=220.0 + i, high=226.0 + i, low=219.0 + i, close=225.0 + i, volume=1000,
            )
            for i in range(60)
        ]

    async def recent_headlines(self, symbol: Symbol) -> list[str]:
        return [
            f"{symbol.code} beats quarterly earnings expectations",
            f"Analysts raise {symbol.code} price target on strong demand",
            "US tech shares rally as inflation cools",
        ]
