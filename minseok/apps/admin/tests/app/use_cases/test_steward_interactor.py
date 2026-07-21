from admin.app.dtos.steward_dto import StewardAccessQuery, StewardQuery
from admin.app.use_cases.steward_interactor import StewardInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


class _StubMembers:
    def __init__(self, permissions):
        self._permissions = permissions

    async def list_user_permissions(self, user_id):
        return self._permissions


async def test_자기소개는_실기능_설명을_반환하고_기록을_남긴다():
    record = _StubRecord()
    interactor = StewardInteractor(record=record, members=_StubMembers([]))
    result = await interactor.introduce_myself(StewardQuery(id=1, name="어드민 콘솔 (admin)"))
    assert result.id == 1
    assert "/admin/dashboard" in result.introduction
    assert record.records[0][0] == "introduce_myself"


async def test_my_access는_보유_권한을_반환한다():
    interactor = StewardInteractor(
        record=_StubRecord(), members=_StubMembers(["members:read", "members:write"])
    )
    result = await interactor.my_access(StewardAccessQuery(user_id=7))
    assert result.user_id == 7
    assert result.permissions == ("members:read", "members:write")


async def test_비관리자는_빈_권한을_받는다():
    interactor = StewardInteractor(record=_StubRecord(), members=_StubMembers([]))
    result = await interactor.my_access(StewardAccessQuery(user_id=8))
    assert result.permissions == ()
