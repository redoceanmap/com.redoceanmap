from __future__ import annotations

import logging

from hub.app.dtos.fundamental_dto import FundamentalSnapshotItem
from hub.app.ports.input.fundamental_ingest_use_case import FundamentalIngestUseCase
from hub.app.ports.output.fundamental_storage_port import FundamentalStoragePort

logger = logging.getLogger(__name__)

_METRICS = ("per", "pbr", "roe", "debt_to_equity", "fcf", "market_cap", "eps", "bps")


class FundamentalIngestInteractor(FundamentalIngestUseCase):
    """펀더멘털 수집 허브 대장 — 유효 스냅샷만 골라 저장 포트(스포크 구현)에 위임한다."""

    def __init__(self, storage: FundamentalStoragePort) -> None:
        self._storage = storage

    async def ingest(self, items: list[FundamentalSnapshotItem]) -> int:
        valid = [
            i for i in items
            if i.ticker.strip() and i.source.strip()
            and any(getattr(i, m) is not None for m in _METRICS)  # 전 지표 결측 스냅샷은 무의미
        ]
        if not valid:
            return 0
        saved = await self._storage.save_many(valid)
        logger.info("[hub-fundamental] 수신 %d건 중 신규 %d건 저장", len(items), saved)
        return saved
