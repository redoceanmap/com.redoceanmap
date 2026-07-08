from __future__ import annotations

import logging

from mail.app.dtos.postman_dto import PostmanQuery, PostmanResponse
from mail.app.ports.input.postman_use_case import PostmanUseCase
from mail.app.ports.output.postman_record_port import PostmanRecordPort

logger = logging.getLogger(__name__)


class PostmanInteractor(PostmanUseCase):
    """수신 메일함 (mail) 대장 — 자기소개 스켈레톤. 담당: 수신 메일의 영속화와 의미 검색."""

    def __init__(self, record: PostmanRecordPort) -> None:
        self._record = record

    async def introduce_myself(self, query: PostmanQuery) -> PostmanResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return PostmanResponse(
            id=query.id,
            name=query.name,
            introduction="수신 메일을 보관·검색합니다. 허브 /automation/mail로 들어온 메일을 bge-m3 임베딩(1024차원)과 함께 inbound_mails에 저장하고, GET /mail/list 최신 목록, GET /mail/search?q= pgvector 코사인 유사도 의미 검색을 제공합니다.",
        )
