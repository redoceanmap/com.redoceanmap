from hub.app.dtos.postmaster_dto import PostmasterQuery
from hub.app.use_cases.postmaster_interactor import PostmasterInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await PostmasterInteractor(record=record).introduce_myself(
        PostmasterQuery(id=7, name="이메일 발송 창구 (hub/email)")
    )
    assert result.id == 7
    assert result.name == "이메일 발송 창구 (hub/email)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
