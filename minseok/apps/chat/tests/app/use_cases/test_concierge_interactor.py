from chat.app.dtos.concierge_dto import ConciergeQuery
from chat.app.use_cases.concierge_interactor import ConciergeInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await ConciergeInteractor(record=record).introduce_myself(
        ConciergeQuery(id=2, name="대화형 분석 창구 (chat)")
    )
    assert result.id == 2
    assert result.name == "대화형 분석 창구 (chat)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
