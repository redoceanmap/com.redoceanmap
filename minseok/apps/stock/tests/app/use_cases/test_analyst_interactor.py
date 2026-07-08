from stock.app.dtos.analyst_dto import AnalystQuery
from stock.app.use_cases.analyst_interactor import AnalystInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await AnalystInteractor(record=record).introduce_myself(
        AnalystQuery(id=4, name="주식 분석 (stock)")
    )
    assert result.id == 4
    assert result.name == "주식 분석 (stock)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
