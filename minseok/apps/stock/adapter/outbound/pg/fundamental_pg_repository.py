from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from stock.adapter.outbound.orm.fundamental_snapshot_orm import FundamentalSnapshotOrm
from stock.app.ports.output.fundamental_repository import FundamentalRepositoryPort
from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot


class FundamentalPgRepository(FundamentalRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_many(self, snapshots: list[FundamentalSnapshot]) -> int:
        if not snapshots:
            return 0
        stmt = (
            pg_insert(FundamentalSnapshotOrm)
            .values([
                {
                    "ticker": s.ticker,
                    "as_of": s.as_of,
                    "source": s.source,
                    "per": s.per,
                    "pbr": s.pbr,
                    "roe": s.roe,
                    "debt_to_equity": s.debt_to_equity,
                    "fcf": s.fcf,
                    "market_cap": s.market_cap,
                    "eps": s.eps,
                    "bps": s.bps,
                }
                for s in snapshots
            ])
            .on_conflict_do_nothing(index_elements=["ticker", "as_of", "source"])
            .returning(FundamentalSnapshotOrm.id)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return len(result.scalars().all())
