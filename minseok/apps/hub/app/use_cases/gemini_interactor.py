from __future__ import annotations

import logging

from hub.app.dtos.gemini_dto import (
    GeminiAnswerQuery,
    GeminiAnswerResponse,
    GeminiQuery,
    GeminiResponse,
)
from hub.app.ports.input.gemini_use_case import GeminiUseCase
from hub.app.ports.output.gemini_answer_port import GeminiAnswerPort
from hub.app.ports.output.gemini_record_port import GeminiRecordPort

logger = logging.getLogger(__name__)


class GeminiInteractor(GeminiUseCase):
    """제미나이 답변기 (hub/gemini) 대장 — 시멘틱 인텐트 3분기(RAG·CRUD·Gemini) 중
    Gemini 분기 담당: 외부 Gemini API로 답변을 생성해 화면(프론트)으로 보낸다."""

    def __init__(self, gemini: GeminiAnswerPort, record: GeminiRecordPort) -> None:
        self._gemini = gemini
        self._record = record

    async def answer(self, query: GeminiAnswerQuery) -> GeminiAnswerResponse:
        result = await self._gemini.generate(query.prompt)
        await self._record.record(
            subject="answer",
            note=f"prompt {len(query.prompt)}자 → {result.model} 답변 {len(result.answer)}자",
        )
        return result

    async def introduce_myself(self, query: GeminiQuery) -> GeminiResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return GeminiResponse(
            id=query.id,
            name=query.name,
            introduction="Google Gemini API로 답변을 생성하는 외부 LLM 창구입니다. "
            "POST /gemini/answer 에 prompt를 보내면 GEMINI_API_KEY로 Gemini를 호출해 "
            "텍스트 답변을 반환합니다. 시멘틱 인텐트 3분기(RAG·CRUD·Gemini) 중 Gemini 분기 "
            "담당이며, 상권/주식 데이터 조회는 하지 않습니다(RAG·CRUD 분기 몫).",
        )