from __future__ import annotations

import logging

from stock.app.ports.input.fundamental_use_case import FundamentalIngestUseCase
from stock.app.ports.output.fundamental_repository import FundamentalRepositoryPort
from stock.domain.entities.fundamental_snapshot import FundamentalSnapshot

logger = logging.getLogger(__name__)


class FundamentalInteractor(FundamentalIngestUseCase):
    """펀더멘털 스냅샷 적재 대장. 저장(중복 무시)만 담당하고 해석은 분석 시점에 한다."""

    def __init__(self, fundamentals: FundamentalRepositoryPort) -> None:
        self._fundamentals = fundamentals

    async def ingest(self, snapshots: list[FundamentalSnapshot]) -> int:
        saved = await self._fundamentals.save_many(snapshots)
        logger.info("[stock-fundamental] 수신 %d건 중 신규 %d건 저장", len(snapshots), saved)
        return saved
