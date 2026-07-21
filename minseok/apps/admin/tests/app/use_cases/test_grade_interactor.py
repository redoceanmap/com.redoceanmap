import pytest

from admin.app.dtos.grade_dto import (
    GradeCreateCommand,
    GradeDeleteCommand,
    GradeUpdateCommand,
)
from admin.app.exceptions import GradeProtectedError, GradeValidationError
from admin.app.use_cases.grade_interactor import GradeInteractor
from hub.app.dtos.grade_dto import GradeInfo


class _StubAudit:
    def __init__(self):
        self.writes = []

    async def write(self, actor_id, action, detail):
        self.writes.append((actor_id, action, detail))

    async def list_recent(self, limit):
        return []


class _StubGradePolicy:
    def __init__(self):
        self.grades = {
            "admin": GradeInfo(
                code="admin",
                name="관리자",
                tabs=("history", "market", "stock", "vision", "automation"),
                member_count=1,
            ),
            "basic": GradeInfo(
                code="basic", name="기본", tabs=("history", "market"), member_count=3
            ),
        }
        self.deleted = []

    async def list_grades(self):
        return list(self.grades.values())

    async def create_grade(self, code, name, tabs):
        if code in self.grades:
            raise ValueError(f"이미 존재하는 등급 코드입니다: {code}")
        info = GradeInfo(code=code, name=name, tabs=tuple(tabs), member_count=0)
        self.grades[code] = info
        return info

    async def update_grade(self, code, name, tabs):
        if code not in self.grades:
            raise ValueError(f"등급이 없습니다: {code}")
        prev = self.grades[code]
        info = GradeInfo(
            code=code,
            name=name if name is not None else prev.name,
            tabs=tuple(tabs) if tabs is not None else prev.tabs,
            member_count=prev.member_count,
        )
        self.grades[code] = info
        return info

    async def delete_grade(self, code):
        if code not in self.grades:
            raise ValueError(f"등급이 없습니다: {code}")
        del self.grades[code]
        self.deleted.append(code)


def _interactor():
    return GradeInteractor(grades=_StubGradePolicy(), audit=_StubAudit())


async def test_등급_생성은_감사_기록을_남긴다():
    interactor = _interactor()
    result = await interactor.create_grade(
        GradeCreateCommand(actor_id=7, code="premium", name="프리미엄", tabs=("history", "stock"))
    )
    assert result.grade.code == "premium"
    assert interactor._audit.writes[0][0] == 7
    assert interactor._audit.writes[0][1] == "grade.create"


async def test_미등록_탭_키는_거부된다():
    interactor = _interactor()
    with pytest.raises(GradeValidationError):
        await interactor.create_grade(
            GradeCreateCommand(actor_id=7, code="premium", name="프리미엄", tabs=("없는탭",))
        )
    with pytest.raises(GradeValidationError):
        await interactor.update_grade(
            GradeUpdateCommand(actor_id=7, code="basic", name=None, tabs=("없는탭",))
        )


async def test_등급_코드_형식이_틀리면_거부된다():
    interactor = _interactor()
    for bad in ("Premium", "1st", "프리미엄", "a" * 51):
        with pytest.raises(GradeValidationError):
            await interactor.create_grade(
                GradeCreateCommand(actor_id=7, code=bad, name="이름", tabs=())
            )


async def test_admin_역할은_삭제와_개명이_차단되고_탭_변경은_허용된다():
    interactor = _interactor()
    with pytest.raises(GradeProtectedError):
        await interactor.delete_grade(GradeDeleteCommand(actor_id=7, code="admin"))
    with pytest.raises(GradeProtectedError):
        await interactor.update_grade(
            GradeUpdateCommand(actor_id=7, code="admin", name="새이름", tabs=None)
        )
    result = await interactor.update_grade(
        GradeUpdateCommand(actor_id=7, code="admin", name=None, tabs=("history",))
    )
    assert result.grade.tabs == ("history",)


async def test_등급_삭제는_회수_규모와_함께_감사_기록된다():
    interactor = _interactor()
    await interactor.delete_grade(GradeDeleteCommand(actor_id=7, code="basic"))
    assert interactor._grades.deleted == ["basic"]
    actor_id, action, detail = interactor._audit.writes[0]
    assert action == "grade.delete"
    assert "revoked_members=3" in detail


async def test_중복_코드_생성은_ValueError로_전파된다():
    interactor = _interactor()
    with pytest.raises(ValueError):
        await interactor.create_grade(
            GradeCreateCommand(actor_id=7, code="basic", name="중복", tabs=())
        )
