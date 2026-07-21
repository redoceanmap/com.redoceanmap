from admin.app.use_cases.area_interactor import AreaInteractor
from hub.app.dtos.commercial_data_dto import AreaOverviewRow


class _StubCommercial:
    async def get_area_overview(self):
        return [
            AreaOverviewRow(
                trdar_code=100,
                trdar_name="성수역",
                gu_name="성동구",
                dong_name="성수동",
                store_count=120,
                closure_rate=4.2,
                monthly_sales=987654321,
            )
        ]


async def test_상권_목록은_허브_집계를_그대로_반환한다():
    result = await AreaInteractor(commercial=_StubCommercial()).list_areas()
    assert len(result.areas) == 1
    assert result.areas[0].trdar_name == "성수역"
    assert result.areas[0].closure_rate == 4.2
