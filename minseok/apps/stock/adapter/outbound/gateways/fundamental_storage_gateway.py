from __future__ import annotations

from hub.app.dtos.fundamental_dto import FundamentalSnapshotItem
from hub.app.ports.output.fundamental_storage_port import FundamentalStoragePort
from stock.app.ports.input.fundamental_use_case import FundamentalIngestUseCase
from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot


class FundamentalStorageGateway(FundamentalStoragePort):
    """허브 FundamentalStoragePort 구현 — 허브 계약 DTO를 도메인 엔티티로 변환해 유스케이스에 위임."""

    def __init__(self, use_case: FundamentalIngestUseCase) -> None:
        self._use_case = use_case

    async def save_many(self, items: list[FundamentalSnapshotItem]) -> int:
        return await self._use_case.ingest([
            FundamentalSnapshot(
                ticker=i.ticker, as_of=i.as_of, source=i.source,
                per=i.per, pbr=i.pbr, roe=i.roe, debt_to_equity=i.debt_to_equity,
                fcf=i.fcf, market_cap=i.market_cap, eps=i.eps, bps=i.bps,
            )
            for i in items
        ])
