from __future__ import annotations

from admin.app.dtos.data_source_dto import DataSourceListResponse
from admin.app.ports.input.data_source_use_case import DataSourceUseCase
from hub.app.dtos.commercial_data_dto import DatasetStat
from hub.app.ports.output.commercial_data_port import CommercialDataPort
from hub.app.ports.output.recommendation_directory_port import RecommendationDirectoryPort


class DataSourceInteractor(DataSourceUseCase):
    """어드민 데이터소스 대장 — market 데이터셋 현황에 추천 기록 카운트를 덧붙인다."""

    def __init__(
        self,
        commercial: CommercialDataPort,
        recommendations: RecommendationDirectoryPort,
    ) -> None:
        self._commercial = commercial
        self._recommendations = recommendations

    async def list_datasets(self) -> DataSourceListResponse:
        datasets = list(await self._commercial.get_dataset_stats())
        rec_stats = await self._recommendations.stats()
        datasets.append(
            DatasetStat(
                key="recommendations",
                name="추천 기록",
                row_count=rec_stats.total,
                latest_label=None,
            )
        )
        return DataSourceListResponse(datasets=datasets)
