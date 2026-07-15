"""semantic_router.py — 시멘틱 게이트웨이(hub/semantic): 의도 분류 후 crud·rag·gemini 3분기."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from hub.adapter.inbound.api.schemas.semantic_schema import (
    SemanticAskResponseSchema,
    SemanticAskSchema,
    SemanticResponseSchema,
)
from hub.app.dtos.semantic_dto import SemanticAskQuery, SemanticQuery
from hub.app.ports.input.semantic_use_case import SemanticUseCase
from hub.app.ports.output.gemini_answer_port import GeminiAnswerError
from hub.dependencies.semantic_provider import get_semantic_use_case

semantic_router = APIRouter(prefix="/semantic", tags=["semantic"])


@semantic_router.get("/myself", response_model=SemanticResponseSchema)
async def introduce_myself(
    semantic: SemanticUseCase = Depends(get_semantic_use_case),
) -> SemanticResponseSchema:
    result = await semantic.introduce_myself(
        SemanticQuery(id=10, name="시멘틱 라우터 (hub/semantic)")
    )
    return SemanticResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )


@semantic_router.post("/ask", response_model=SemanticAskResponseSchema)
async def ask(
    body: SemanticAskSchema,
    semantic: SemanticUseCase = Depends(get_semantic_use_case),
) -> SemanticAskResponseSchema:
    try:
        result = await semantic.ask(SemanticAskQuery(prompt=body.prompt))
    except GeminiAnswerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return SemanticAskResponseSchema(
        destination=result.destination,
        entities=list(result.entities),
        answer=result.answer,
    )
