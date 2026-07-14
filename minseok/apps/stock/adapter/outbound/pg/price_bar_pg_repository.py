from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from stock.adapter.outbound.orm.price_bar_orm import PriceBarOrm
from stock.app.dtos.price_bar_dto import PriceBarCoverage
from stock.app.ports.output.price_bar_repository import PriceBarRepositoryPort
from stock.domain.entities.price_bar import PriceBar


_CHUNK = 5000  # 행당 8파라미터 × 5000 = 40,000 < psycopg 상한(65,535)


class PriceBarPgRepository(PriceBarRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_many(self, bars: list[PriceBar]) -> int:
        if not bars:
            return 0
        saved = 0
        for start in range(0, len(bars), _CHUNK):
            stmt = (
                pg_insert(PriceBarOrm)
                .values([
                    {
                        "ticker": b.ticker,
                        "timeframe": b.timeframe,
                        "ts": b.ts,
                        "open": b.open,
                        "high": b.high,
                        "low": b.low,
                        "close": b.close,
                        "volume": b.volume,
                    }
                    for b in bars[start:start + _CHUNK]
                ])
                .on_conflict_do_nothing(index_elements=["ticker", "timeframe", "ts"])
                .returning(PriceBarOrm.id)
            )
            result = await self._session.execute(stmt)
            saved += len(result.scalars().all())
        await self._session.commit()
        return saved

    async def coverage(self) -> list[PriceBarCoverage]:
        stmt = (
            select(
                PriceBarOrm.ticker,
                PriceBarOrm.timeframe,
                func.min(PriceBarOrm.ts),
                func.max(PriceBarOrm.ts),
                func.count(PriceBarOrm.id),
            )
            .group_by(PriceBarOrm.ticker, PriceBarOrm.timeframe)
            .order_by(PriceBarOrm.ticker, PriceBarOrm.timeframe)
        )
        result = await self._session.execute(stmt)
        return [
            PriceBarCoverage(
                ticker=ticker, timeframe=timeframe, first_ts=first, last_ts=last, bars=count
            )
            for ticker, timeframe, first, last, count in result.all()
        ]
