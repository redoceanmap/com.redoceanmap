from __future__ import annotations

from fastapi import APIRouter, Depends

from mail.adapter.inbound.api.schemas.postman_schema import PostmanResponseSchema
from mail.app.dtos.postman_dto import PostmanQuery
from mail.app.ports.input.postman_use_case import PostmanUseCase
from mail.dependencies.postman_provider import get_postman_use_case

postman_router = APIRouter(prefix="/mail", tags=["mail"])


@postman_router.get("/myself", response_model=PostmanResponseSchema)
async def introduce_myself(
    postman: PostmanUseCase = Depends(get_postman_use_case)
) -> PostmanResponseSchema:
    result = await postman.introduce_myself(
        PostmanQuery(
            id=8,
            name="수신 메일함 (mail)"
        )
    )
    return PostmanResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
