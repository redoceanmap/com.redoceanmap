from __future__ import annotations

import logging

from hub.app.dtos.semantic_dto import (
    SemanticAskQuery,
    SemanticAskResponse,
    SemanticQuery,
    SemanticResponse,
)
from hub.app.ports.input.semantic_use_case import SemanticUseCase
from hub.app.ports.output.gemini_answer_port import GeminiAnswerPort
from hub.app.ports.output.market_news_search_port import MarketNewsSearchPort
from hub.app.ports.output.semantic_llm_port import SemanticLlmPort
from hub.app.ports.output.semantic_record_port import SemanticRecordPort

logger = logging.getLogger(__name__)

_DESTINATIONS = {"crud", "rag", "gemini"}


class SemanticInteractor(SemanticUseCase):
    """시멘틱 라우터 (hub/semantic) 대장 — 단일 모델(EXAONE 7.8B)이 의도 분류와
    RAG 답변을 겸하고(동적 프롬프팅, QLoRA 없음 — PoC), 흐름 통제는 코드가 한다."""

    def __init__(
        self,
        llm: SemanticLlmPort,
        gemini: GeminiAnswerPort,
        market_news: MarketNewsSearchPort,
        record: SemanticRecordPort,
    ) -> None:
        self._llm = llm
        self._gemini = gemini
        self._market_news = market_news
        self._record = record

    async def ask(self, query: SemanticAskQuery) -> SemanticAskResponse:
        route = await self._llm.classify(query.prompt)
        destination = route.destination if route.destination in _DESTINATIONS else "rag"

        if destination == "crud":
            targets = ", ".join(route.entities) or query.prompt[:30]
            answer = f"[CRUD PoC] '{targets}' 관련 데이터 조작 의도를 감지했습니다. 실제 실행은 미구현입니다."
        elif destination == "gemini":
            answer = (await self._gemini.generate(query.prompt)).answer
        else:  # rag
            hits = await self._market_news.search(query.prompt, limit=4)
            if not hits:
                answer = "관련 정보를 상권 뉴스 코퍼스에서 찾지 못해 답변을 드릴 수 없습니다. (근거 없는 추측 금지 — 가드레일)"
            else:
                context = "\n".join(
                    f"- {hit.title} ({hit.area_tag or '공통'}"
                    + (f", {hit.published_at:%Y-%m-%d})" if hit.published_at else ")")
                    for hit in hits
                )
                answer = await self._llm.answer_grounded(query.prompt, context)

        await self._record.record(
            subject="ask",
            note=f"{destination} | entities={list(route.entities)} | 답변 {len(answer)}자",
        )
        return SemanticAskResponse(
            destination=destination, entities=route.entities, answer=answer
        )

    async def introduce_myself(self, query: SemanticQuery) -> SemanticResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return SemanticResponse(
            id=query.id,
            name=query.name,
            introduction="질문 의도를 분류해 3분기로 라우팅하는 시멘틱 게이트웨이입니다(PoC). "
            "POST /semantic/ask 에 prompt를 보내면 EXAONE 7.8B가 의도를 crud·rag·gemini로 "
            "분류하고 — crud는 감지만(실행 미구현), rag는 상권 뉴스 근거 답변(근거 없으면 "
            "답변 거부), gemini는 외부 Gemini API 답변을 반환합니다.",
        )
