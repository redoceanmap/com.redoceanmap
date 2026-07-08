from hub.app.dtos.dispatcher_dto import DispatcherQuery
from hub.app.use_cases.dispatcher_interactor import DispatcherInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await DispatcherInteractor(record=record).introduce_myself(
        DispatcherQuery(id=6, name="자동화 창구 (hub/automation)")
    )
    assert result.id == 6
    assert result.name == "자동화 창구 (hub/automation)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
