from __future__ import annotations

import logging

from chat.app.dtos.concierge_dto import ConciergeQuery, ConciergeResponse
from chat.app.ports.input.concierge_use_case import ConciergeUseCase
from chat.app.ports.output.concierge_record_port import ConciergeRecordPort

logger = logging.getLogger(__name__)


class ConciergeInteractor(ConciergeUseCase):
    """대화형 분석 창구 (chat) 대장 — 자기소개 스켈레톤. 담당: 대화 의도 분류(phase0)와 최종 서술의 창구."""

    def __init__(self, record: ConciergeRecordPort) -> None:
        self._record = record

    async def introduce_myself(self, query: ConciergeQuery) -> ConciergeResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return ConciergeResponse(
            id=query.id,
            name=query.name,
            introduction="대화로 분석을 제공합니다. POST /chat/ask는 질문 의도를 분류해(phase0) 상권 질문은 2단계 추론으로 추천을, 주식 질문은 허브 StockAnalysisPort로 분석 카드를 반환하고, POST /chat/stream은 SSE로 토큰 스트리밍합니다. 대화는 conversations/messages에 보존됩니다.",
        )
