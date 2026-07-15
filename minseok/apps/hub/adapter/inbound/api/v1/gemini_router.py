"""gemini_router.py — 외부 Gemini API 답변 창구(hub/gemini)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from hub.adapter.inbound.api.schemas.gemini_schema import (
    GeminiAnswerResponseSchema,
    GeminiAnswerSchema,
    GeminiResponseSchema,
)
from hub.app.dtos.gemini_dto import GeminiAnswerQuery, GeminiQuery
from hub.app.ports.input.gemini_use_case import GeminiUseCase
from hub.app.ports.output.gemini_answer_port import GeminiAnswerError
from hub.dependencies.gemini_provider import get_gemini_use_case

gemini_router = APIRouter(prefix="/gemini", tags=["gemini"])


@gemini_router.get("/myself", response_model=GeminiResponseSchema)
async def introduce_myself(
    gemini: GeminiUseCase = Depends(get_gemini_use_case),
) -> GeminiResponseSchema:
    result = await gemini.introduce_myself(
        GeminiQuery(id=9, name="제미나이 답변기 (hub/gemini)")
    )
    return GeminiResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )


@gemini_router.post("/answer", response_model=GeminiAnswerResponseSchema)
async def answer(
    body: GeminiAnswerSchema,
    gemini: GeminiUseCase = Depends(get_gemini_use_case),
) -> GeminiAnswerResponseSchema:
    try:
        result = await gemini.answer(GeminiAnswerQuery(prompt=body.prompt))
    except GeminiAnswerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return GeminiAnswerResponseSchema(answer=result.answer, model=result.model)
