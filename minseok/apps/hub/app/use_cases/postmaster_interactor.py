from __future__ import annotations

import logging

from hub.app.dtos.postmaster_dto import PostmasterQuery, PostmasterResponse
from hub.app.ports.input.postmaster_use_case import PostmasterUseCase
from hub.app.ports.output.postmaster_record_port import PostmasterRecordPort

logger = logging.getLogger(__name__)


class PostmasterInteractor(PostmasterUseCase):
    """이메일 발송 창구 (hub/email) 대장 — 자기소개 스켈레톤. 담당: 이메일 요청의 온톨로지 지시 합성과 위임."""

    def __init__(self, record: PostmasterRecordPort) -> None:
        self._record = record

    async def introduce_myself(self, query: PostmasterQuery) -> PostmasterResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return PostmasterResponse(
            id=query.id,
            name=query.name,
            introduction="이메일 발송 요청을 받습니다. POST /email/request — 내용을 허브 온톨로지 규범(정중하고 간결한 한국어, 인사말→본문→맺음말)으로 다듬어 chat 게이트웨이에 위임하고, 7.8B가 작성한 메일이 n8n을 거쳐 Gmail로 발송됩니다.",
        )
