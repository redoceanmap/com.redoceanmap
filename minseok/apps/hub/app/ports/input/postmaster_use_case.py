from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.postmaster_dto import PostmasterQuery, PostmasterResponse


class PostmasterUseCase(ABC):
    """이메일 발송 창구 (hub/email) 유스케이스 — 이메일 요청의 온톨로지 지시 합성과 위임."""

    @abstractmethod
    async def introduce_myself(self, query: PostmasterQuery) -> PostmasterResponse:
        """이메일 발송 창구 (hub/email)의 자기소개 메소드."""
        ...
