from __future__ import annotations

from abc import ABC, abstractmethod

from mail.app.dtos.postman_dto import PostmanQuery, PostmanResponse


class PostmanUseCase(ABC):
    """수신 메일함 (mail) 유스케이스 — 수신 메일의 영속화와 의미 검색."""

    @abstractmethod
    async def introduce_myself(self, query: PostmanQuery) -> PostmanResponse:
        """수신 메일함 (mail)의 자기소개 메소드."""
        ...
