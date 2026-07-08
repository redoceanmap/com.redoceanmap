from __future__ import annotations

import logging

from recommendation.app.dtos.curator_dto import CuratorQuery, CuratorResponse
from recommendation.app.ports.input.curator_use_case import CuratorUseCase
from recommendation.app.ports.output.curator_record_port import CuratorRecordPort

logger = logging.getLogger(__name__)


class CuratorInteractor(CuratorUseCase):
    """추천 기록 (recommendation) 대장 — 자기소개 스켈레톤. 담당: 추천 이력의 보관과 재조회."""

    def __init__(self, record: CuratorRecordPort) -> None:
        self._record = record

    async def introduce_myself(self, query: CuratorQuery) -> CuratorResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return CuratorResponse(
            id=query.id,
            name=query.name,
            introduction="chat이 생성한 상권 추천을 영속화하고 조회합니다. GET /recommendations 전체 목록, GET /recommendations/conversation/{id} 대화별 추천 기록을 제공합니다. 기록은 허브 RecommendationRecordPort를 통해 들어옵니다.",
        )
