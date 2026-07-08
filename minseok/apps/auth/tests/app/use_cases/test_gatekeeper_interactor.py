from auth.app.dtos.gatekeeper_dto import GatekeeperQuery
from auth.app.use_cases.gatekeeper_interactor import GatekeeperInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await GatekeeperInteractor(record=record).introduce_myself(
        GatekeeperQuery(id=1, name="인증 서비스 (auth)")
    )
    assert result.id == 1
    assert result.name == "인증 서비스 (auth)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"
