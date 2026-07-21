from __future__ import annotations

from fastapi import Depends

from admin.app.ports.input.data_source_use_case import DataSourceUseCase
from admin.app.use_cases.data_source_interactor import DataSourceInteractor
from hub.app.ports.output.commercial_data_port import CommercialDataPort
from hub.app.ports.output.price_bar_storage_port import PriceBarStoragePort
from hub.app.ports.output.recommendation_directory_port import RecommendationDirectoryPort
from hub.dependencies.commercial_data_provider import get_commercial_data_port
from hub.dependencies.price_bar_ingest_provider import get_price_bar_storage_port
from hub.dependencies.recommendation_directory_provider import get_recommendation_directory_port


def get_data_source_use_case(
    commercial: CommercialDataPort = Depends(get_commercial_data_port),
    recommendations: RecommendationDirectoryPort = Depends(get_recommendation_directory_port),
    prices: PriceBarStoragePort = Depends(get_price_bar_storage_port),
) -> DataSourceUseCase:
    return DataSourceInteractor(
        commercial=commercial, recommendations=recommendations, prices=prices
    )
