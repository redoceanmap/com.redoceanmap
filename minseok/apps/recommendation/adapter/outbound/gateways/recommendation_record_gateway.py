from __future__ import annotations

from hub.app.dtos.recommendation_record_dto import RecommendedArea
from hub.app.ports.output.recommendation_record_port import RecommendationRecordPort
from recommendation.app.dtos.recommendation_dto import RecommendationDraft
from recommendation.app.ports.input.recommendation_use_case import RecommendationUseCase


class RecommendationRecordGateway(RecommendationRecordPort):
    """허브의 RecommendationRecordPort를 recommendation(스포크)이 구현한다.

    스포크 → 허브 추상에만 의존(스타 토폴로지 허용). 허브 계약 DTO(RecommendedArea)를
    도메인 초안(RecommendationDraft)으로 변환해 기존 유스케이스에 위임한다.
    """

    def __init__(self, use_case: RecommendationUseCase) -> None:
        self._use_case = use_case

    async def record(
        self, conversation_id: int | None, areas: list[RecommendedArea]
    ) -> None:
        drafts = [
            RecommendationDraft(
                trdar_code=a.trdar_code,
                trdar_name=a.trdar_name,
                district_name=a.district_name,
                category=a.category,
                reason=a.reason,
                lat=a.lat,
                lng=a.lng,
            )
            for a in areas
        ]
        await self._use_case.record(conversation_id, drafts)
