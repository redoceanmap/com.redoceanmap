from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.semantic_dto import SemanticRoute


class SemanticLlmPort(ABC):
    """시멘틱 라우터의 LLM 아웃바운드 포트 — 단일 모델 2역(분류 + 근거 답변).

    구현(EXAONE 7.8B/오케스트레이터 어댑터)은 어댑터가 제공. 분류 실패는 예외가 아니라
    rag 폴백 라우트로 알린다(열화 동작 — 게이트웨이는 멈추지 않는다).
    """

    @abstractmethod
    async def classify(self, question: str) -> SemanticRoute:
        """질문 의도를 분류한다. 파싱 실패 시 destination='rag' 폴백을 반환한다."""
        ...

    @abstractmethod
    async def answer_grounded(self, question: str, context: str) -> str:
        """주어진 컨텍스트에만 근거해 답변을 생성한다(환각 금지 프롬프트)."""
        ...
