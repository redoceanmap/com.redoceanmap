from __future__ import annotations

from dataclasses import dataclass

from hub.app.dtos.recommendation_directory_dto import RecommendationInfo


@dataclass(frozen=True)
class RecommendationLogQuery:
    limit: int


@dataclass(frozen=True)
class RecommendationLogResponse:
    total: int
    today: int
    items: list[RecommendationInfo]
