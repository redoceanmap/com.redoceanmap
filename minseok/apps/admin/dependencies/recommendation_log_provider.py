from __future__ import annotations

from fastapi import Depends

from admin.app.ports.input.recommendation_log_use_case import RecommendationLogUseCase
from admin.app.use_cases.recommendation_log_interactor import RecommendationLogInteractor
from hub.app.ports.output.recommendation_directory_port import RecommendationDirectoryPort
from hub.dependencies.recommendation_directory_provider import get_recommendation_directory_port


def get_recommendation_log_use_case(
    recommendations: RecommendationDirectoryPort = Depends(get_recommendation_directory_port),
) -> RecommendationLogUseCase:
    return RecommendationLogInteractor(recommendations=recommendations)
