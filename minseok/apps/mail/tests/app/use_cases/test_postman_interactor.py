from mail.app.dtos.postman_dto import PostmanQuery
from mail.app.use_cases.postman_interactor import PostmanInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await PostmanInteractor(record=record).introduce_myself(
        PostmanQuery(id=8, name="수신 메일함 (mail)")
    )
    assert result.id == 8
    assert result.name == "수신 메일함 (mail)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
