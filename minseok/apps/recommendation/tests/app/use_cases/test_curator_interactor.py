from recommendation.app.dtos.curator_dto import CuratorQuery
from recommendation.app.use_cases.curator_interactor import CuratorInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await CuratorInteractor(record=record).introduce_myself(
        CuratorQuery(id=5, name="추천 기록 (recommendation)")
    )
    assert result.id == 5
    assert result.name == "추천 기록 (recommendation)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
