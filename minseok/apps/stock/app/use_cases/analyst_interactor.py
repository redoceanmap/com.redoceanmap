from __future__ import annotations

import logging

from stock.app.dtos.analyst_dto import AnalystQuery, AnalystResponse
from stock.app.ports.input.analyst_use_case import AnalystUseCase
from stock.app.ports.output.analyst_record_port import AnalystRecordPort

logger = logging.getLogger(__name__)


class AnalystInteractor(AnalystUseCase):
    """주식 분석 (stock) 대장 — 자기소개 스켈레톤. 담당: 지표+뉴스 결합 분석 — 백테스트로 검증되는 신호만."""

    def __init__(self, record: AnalystRecordPort) -> None:
        self._record = record

    async def introduce_myself(self, query: AnalystQuery) -> AnalystResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return AnalystResponse(
            id=query.id,
            name=query.name,
            introduction="종목의 방향 신호를 분석합니다. POST /stock/analyze — yfinance 시세(한국 .KS/.KQ + 미국)로 RSI·이동평균·지지/저항을 계산하고, 수집 뉴스와 EXAONE 감성 분석을 결합해 UP/DOWN/NEUTRAL 신호를 냅니다. 매매 지시는 하지 않습니다.",
        )
