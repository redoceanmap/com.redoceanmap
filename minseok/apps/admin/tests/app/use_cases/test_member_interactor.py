from datetime import datetime, timezone

import pytest

from admin.app.dtos.member_dto import (
    MemberActionCommand,
    MemberListQuery,
    RoleChangeCommand,
    SuspendCommand,
)
from admin.app.use_cases.member_interactor import MemberInteractor
from hub.app.dtos.member_directory_dto import MemberInfo, MemberPage, RoleInfo


def _member(user_id=1, roles=()):
    return MemberInfo(
        id=user_id,
        email="a@b.c",
        name="테스터",
        joined_at=None,
        marketing_agreed=False,
        roles=tuple(roles),
    )


class _StubAudit:
    def __init__(self):
        self.writes = []

    async def write(self, actor_id, action, detail):
        self.writes.append((actor_id, action, detail))

    async def list_recent(self, limit):
        return []


class _StubDirectory:
    def __init__(self):
        self.calls = []

    async def list_members(self, search, limit, offset):
        self.calls.append(("list", search, limit, offset))
        return MemberPage(total=1, items=[_member()])

    async def list_roles(self):
        return [RoleInfo(code="admin", name="관리자", permissions=("members:read",))]

    async def grant_role(self, user_id, role_code):
        if user_id == 999:
            raise ValueError("유저가 없습니다")
        return _member(user_id, roles=[role_code])

    async def revoke_role(self, user_id, role_code):
        return _member(user_id, roles=[])

    async def suspend(self, user_id, reason):
        return MemberInfo(
            id=user_id,
            email="a@b.c",
            name="테스터",
            joined_at=None,
            marketing_agreed=False,
            roles=(),
            suspended_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
        )

    async def reinstate(self, user_id):
        return _member(user_id)

    async def revoke_sessions(self, user_id):
        return 2

    async def withdraw(self, user_id):
        return MemberInfo(
            id=user_id,
            email=f"deleted-{user_id}@removed.local",
            name="탈퇴회원",
            joined_at=None,
            marketing_agreed=False,
            roles=(),
            deleted_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
        )


async def test_목록은_limit을_상한으로_보정한다():
    directory = _StubDirectory()
    interactor = MemberInteractor(members=directory, audit=_StubAudit())
    await interactor.list_members(MemberListQuery(search=None, limit=9999, offset=-5))
    assert directory.calls[0] == ("list", None, 100, 0)


async def test_역할_부여는_갱신된_회원을_반환하고_감사_기록을_남긴다():
    audit = _StubAudit()
    interactor = MemberInteractor(members=_StubDirectory(), audit=audit)
    result = await interactor.grant_role(RoleChangeCommand(actor_id=7, user_id=1, role_code="admin"))
    assert result.member.roles == ("admin",)
    assert audit.writes == [(7, "role.grant", "user=1(a@b.c) role=admin")]


async def test_없는_유저_부여는_ValueError를_전파하고_기록하지_않는다():
    audit = _StubAudit()
    interactor = MemberInteractor(members=_StubDirectory(), audit=audit)
    with pytest.raises(ValueError):
        await interactor.grant_role(RoleChangeCommand(actor_id=7, user_id=999, role_code="admin"))
    assert audit.writes == []


async def test_역할_회수는_빈_역할을_반환하고_감사_기록을_남긴다():
    audit = _StubAudit()
    interactor = MemberInteractor(members=_StubDirectory(), audit=audit)
    result = await interactor.revoke_role(RoleChangeCommand(actor_id=7, user_id=1, role_code="admin"))
    assert result.member.roles == ()
    assert audit.writes[0][1] == "role.revoke"


async def test_정지는_사유와_함께_감사_기록을_남긴다():
    audit = _StubAudit()
    interactor = MemberInteractor(members=_StubDirectory(), audit=audit)
    result = await interactor.suspend(SuspendCommand(actor_id=7, user_id=1, reason="약관 위반"))
    assert result.member.suspended_at is not None
    assert audit.writes[0][1] == "member.suspend"
    assert "약관 위반" in audit.writes[0][2]


async def test_세션_폐기는_건수를_반환하고_기록한다():
    audit = _StubAudit()
    interactor = MemberInteractor(members=_StubDirectory(), audit=audit)
    result = await interactor.revoke_sessions(MemberActionCommand(actor_id=7, user_id=1))
    assert result.revoked == 2
    assert audit.writes[0][1] == "member.sessions.revoke"


async def test_탈퇴는_익명화된_회원을_반환하고_기록한다():
    audit = _StubAudit()
    interactor = MemberInteractor(members=_StubDirectory(), audit=audit)
    result = await interactor.withdraw(MemberActionCommand(actor_id=7, user_id=5))
    assert result.member.deleted_at is not None
    assert result.member.email == "deleted-5@removed.local"
    assert audit.writes[0][1] == "member.withdraw"


async def test_자기_자신은_정지할_수_없다():
    audit = _StubAudit()
    interactor = MemberInteractor(members=_StubDirectory(), audit=audit)
    with pytest.raises(ValueError):
        await interactor.suspend(SuspendCommand(actor_id=7, user_id=7, reason=""))
    assert audit.writes == []


async def test_자기_자신은_탈퇴_처리할_수_없다():
    audit = _StubAudit()
    interactor = MemberInteractor(members=_StubDirectory(), audit=audit)
    with pytest.raises(ValueError):
        await interactor.withdraw(MemberActionCommand(actor_id=7, user_id=7))
    assert audit.writes == []
