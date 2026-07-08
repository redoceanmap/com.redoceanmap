from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from mail.adapter.inbound.api.schemas.judge_schema import JudgeResponseSchema
from mail.app.dtos.judge_dto import JudgeQuery
from mail.app.ports.input.judge_use_case import JudgeUseCase
from mail.dependencies.judge_provider import get_judge_use_case

logger = logging.getLogger(__name__)

'''
메일 판단기 (mail/judge)
단서(유사 메일)를 종합해 일반 메일의 최종 판단을 내리는 핵심 추론 담당.
참고 배역 명세: apps/mail/_docs/mail-agent-casting.md (detective_holmes_judge)
트리아지 설계안(watcher_router.md)의 Case A — 왓처가 분류한 일반 메일을 넘겨받아
결론을 내리는 자리(미구현, 자기소개 스켈레톤 단계).
'''

judge_router = APIRouter(prefix="/judge", tags=["judge"])


@judge_router.get("/myself", response_model=JudgeResponseSchema)
async def introduce_myself(
    judge: JudgeUseCase = Depends(get_judge_use_case)
) -> JudgeResponseSchema:
    result = await judge.introduce_myself(
        JudgeQuery(
            id=9,
            name="메일 판단기 (mail/judge)"
        )
    )
    return JudgeResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
