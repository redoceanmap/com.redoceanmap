from __future__ import annotations

import logging

from hub.app.dtos.dispatcher_dto import DispatcherQuery, DispatcherResponse
from hub.app.ports.input.dispatcher_use_case import DispatcherUseCase
from hub.app.ports.output.dispatcher_record_port import DispatcherRecordPort

logger = logging.getLogger(__name__)


class DispatcherInteractor(DispatcherUseCase):
    """자동화 창구 (hub/automation) 대장 — 자기소개 스켈레톤. 담당: 자동화 단일 창구(/automation/*)의 관제."""

    def __init__(self, record: DispatcherRecordPort) -> None:
        self._record = record

    async def introduce_myself(self, query: DispatcherQuery) -> DispatcherResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return DispatcherResponse(
            id=query.id,
            name=query.name,
            introduction="n8n 자동화의 단일 인바운드 창구입니다. POST /automation/news 뉴스 적재(→stock), POST /automation/mail 수신 메일 저장(→mail, 임베딩 포함), POST /automation/stock-scan 관심 종목 일괄 스캔을 제공하며, X-Webhook-Token으로 호출자를 검증합니다.",
        )
