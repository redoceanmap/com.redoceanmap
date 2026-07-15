from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.semantic_dto import (
    SemanticAskQuery,
    SemanticAskResponse,
    SemanticQuery,
    SemanticResponse,
)


class SemanticUseCase(ABC):
    """시멘틱 라우터 (hub/semantic) 유스케이스 — 의도 분류 후 3분기(crud·rag·gemini) 응답."""

    @abstractmethod
    async def introduce_myself(self, query: SemanticQuery) -> SemanticResponse:
        """시멘틱 라우터 (hub/semantic)의 자기소개 메소드."""
        ...

    @abstractmethod
    async def ask(self, query: SemanticAskQuery) -> SemanticAskResponse:
        """질문 의도를 분류하고 해당 분기의 답변을 생성한다."""
        ...
