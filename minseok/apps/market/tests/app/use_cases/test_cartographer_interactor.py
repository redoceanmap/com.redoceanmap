from market.app.dtos.cartographer_dto import CartographerQuery
from market.app.use_cases.cartographer_interactor import CartographerInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await CartographerInteractor(record=record).introduce_myself(
        CartographerQuery(id=3, name="상권 데이터 조회 (market)")
    )
    assert result.id == 3
    assert result.name == "상권 데이터 조회 (market)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
