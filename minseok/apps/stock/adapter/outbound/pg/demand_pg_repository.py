from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from stock.adapter.outbound.orm.stock_demand_orm import StockDemandOrm
from stock.app.ports.output.demand_record_port import DemandRecordPort


class DemandPgRepository(DemandRecordPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, ticker: str) -> None:
        now = datetime.now(UTC)
        stmt = pg_insert(StockDemandOrm).values(
            ticker=ticker.strip().upper(), ask_count=1, last_asked_at=now,
        ).on_conflict_do_update(
            index_elements=["ticker"],
            set_={"ask_count": StockDemandOrm.ask_count + 1, "last_asked_at": now},
        )
        try:
            await self._session.execute(stmt)
            await self._session.commit()
        except Exception:
            # 실패 트랜잭션을 세션에 남기면 같은 세션을 쓰는 후속 조회(뉴스 등)까지
            # PendingRollbackError로 오염된다 — 되돌린 뒤 알린다(로깅은 호출자 몫).
            await self._session.rollback()
            raise
