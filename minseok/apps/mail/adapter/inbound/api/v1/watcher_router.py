from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from mail.adapter.inbound.api.schemas.watcher_schema import (
    ScreenRequestSchema,
    ScreenResponseSchema,
    WatcherResponseSchema,
)
from mail.app.dtos.watcher_dto import WatcherQuery
from mail.app.ports.input.watcher_use_case import WatcherUseCase
from mail.dependencies.watcher_provider import get_watcher_use_case

logger = logging.getLogger(__name__)

'''
수신 분류기 (mail/watcher)
수신 메일을 관찰·기록하고 1차 분류(트리아지)하는 관문.
설계안: apps/mail/_docs/watcher_router.md — 일반 메일은 mail 유스케이스로 종결,
중요/보고서 메일은 허브 경유 LLM 오케스트레이터로 격상(미구현, 자기소개 스켈레톤 단계).
'''

watcher_router = APIRouter(prefix="/watcher", tags=["watcher"])


@watcher_router.get("/myself", response_model=WatcherResponseSchema)
async def introduce_myself(
    watcher: WatcherUseCase = Depends(get_watcher_use_case)
) -> WatcherResponseSchema:
    result = await watcher.introduce_myself(
        WatcherQuery(
            id=10,
            name="수신 분류기 (mail/watcher)"
        )
    )
    return WatcherResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )


@watcher_router.post("/screen", response_model=ScreenResponseSchema, summary="유해 한국어 스크리닝")
async def screen(
    body: ScreenRequestSchema,
    watcher: WatcherUseCase = Depends(get_watcher_use_case)
) -> ScreenResponseSchema:
    """KcELECTRA+Unsmile v1 점수에 도메인 정책(카테고리 9종, 임계값 0.5)을 적용해 판정한다."""
    result = await watcher.screen(body.text)
    return ScreenResponseSchema(
        isAbusive=result.is_abusive,
        categories=list(result.categories),
        scores=result.scores,
    )
