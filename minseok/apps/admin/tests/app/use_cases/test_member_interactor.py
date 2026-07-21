import pytest

from admin.app.dtos.member_dto import MemberListQuery, RoleChangeCommand
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


async def test_목록은_limit을_상한으로_보정한다():
    directory = _StubDirectory()
    interactor = MemberInteractor(members=directory)
    await interactor.list_members(MemberListQuery(search=None, limit=9999, offset=-5))
    assert directory.calls[0] == ("list", None, 100, 0)


async def test_역할_부여는_갱신된_회원을_반환한다():
    interactor = MemberInteractor(members=_StubDirectory())
    result = await interactor.grant_role(RoleChangeCommand(user_id=1, role_code="admin"))
    assert result.member.roles == ("admin",)


async def test_없는_유저_부여는_ValueError를_전파한다():
    interactor = MemberInteractor(members=_StubDirectory())
    with pytest.raises(ValueError):
        await interactor.grant_role(RoleChangeCommand(user_id=999, role_code="admin"))


async def test_역할_회수는_빈_역할을_반환한다():
    interactor = MemberInteractor(members=_StubDirectory())
    result = await interactor.revoke_role(RoleChangeCommand(user_id=1, role_code="admin"))
    assert result.member.roles == ()
