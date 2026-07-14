"""postmaster_router.py — 이메일 발송 창구(hub/email)의 자기소개."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.postmaster_schema import PostmasterResponseSchema
from hub.app.dtos.postmaster_dto import PostmasterQuery
from hub.app.ports.input.postmaster_use_case import PostmasterUseCase
from hub.dependencies.postmaster_provider import get_postmaster_use_case

postmaster_router = APIRouter(prefix="/email", tags=["hub-email"])


@postmaster_router.get("/myself", response_model=PostmasterResponseSchema)
async def introduce_myself(
    postmaster: PostmasterUseCase = Depends(get_postmaster_use_case)
) -> PostmasterResponseSchema:
    result = await postmaster.introduce_myself(
        PostmasterQuery(
            id=7,
            name="이메일 발송 창구 (hub/email)"
        )
    )
    return PostmasterResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
