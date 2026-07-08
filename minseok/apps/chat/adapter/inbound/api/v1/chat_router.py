import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from chat.adapter.inbound.api.schemas.chat_schema import AskRequest
from chat.app.dtos.chat_dto import AskResponse
from chat.app.exceptions import (
    ChatError,
    CommercialDataUnavailableError,
    InvalidLLMResponseError,
    NoValidAreaError,
)
from chat.app.ports.input.chat_use_case import ChatUseCase
from chat.dependencies.chat_provider import get_chat_use_case
from chat.adapter.inbound.api.schemas.concierge_schema import ConciergeResponseSchema
from chat.app.dtos.concierge_dto import ConciergeQuery
from chat.app.ports.input.concierge_use_case import ConciergeUseCase
from chat.dependencies.concierge_provider import get_concierge_use_case

chat_router = APIRouter(prefix="/chat", tags=["chat"])

# 앱 계층 예외 → HTTP 상태코드 변환은 인바운드 어댑터의 책임
_STATUS_BY_ERROR: dict[type[ChatError], int] = {
    CommercialDataUnavailableError: 503,
    NoValidAreaError: 422,
    InvalidLLMResponseError: 500,
}


@chat_router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
):
    try:
        return await use_case.ask(body.prompt, body.conversationId)
    except ChatError as e:
        raise HTTPException(status_code=_STATUS_BY_ERROR[type(e)], detail=e.detail)


@chat_router.post("/stream")
async def stream(
    body: AskRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
):
    """대화형 답변을 SSE(text/event-stream)로 토큰 스트리밍한다."""
    async def event_gen():
        async for event in use_case.stream_reply(body.prompt, body.conversationId):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@chat_router.get("/myself", response_model=ConciergeResponseSchema)
async def introduce_myself(
    concierge: ConciergeUseCase = Depends(get_concierge_use_case)
) -> ConciergeResponseSchema:
    result = await concierge.introduce_myself(
        ConciergeQuery(
            id=2,
            name="대화형 분석 창구 (chat)"
        )
    )
    return ConciergeResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
