from __future__ import annotations

import re

from admin.app.dtos.grade_dto import (
    GradeCreateCommand,
    GradeDeleteCommand,
    GradeListResponse,
    GradeResponse,
    GradeUpdateCommand,
)
from admin.app.exceptions import GradeProtectedError, GradeValidationError
from admin.app.ports.input.grade_use_case import GradeUseCase
from admin.app.ports.output.audit_log_port import AuditLogPort
from hub.app.ports.output.grade_policy_port import GradePolicyPort
from hub.domain.navigation.tab_ontology import TAB_KEYS

CODE_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,49}$")
PROTECTED_CODE = "admin"  # 콘솔 잠금 방지 — 삭제·개명 불가(탭 변경은 허용)


class GradeInteractor(GradeUseCase):
    """어드민 등급 관리 대장 — 허브 GradePolicyPort에 위임하고 변경 행위를 감사 기록한다."""

    def __init__(self, grades: GradePolicyPort, audit: AuditLogPort) -> None:
        self._grades = grades
        self._audit = audit

    async def list_grades(self) -> GradeListResponse:
        return GradeListResponse(grades=await self._grades.list_grades())

    async def create_grade(self, command: GradeCreateCommand) -> GradeResponse:
        if not CODE_PATTERN.match(command.code):
            raise GradeValidationError(
                "등급 코드는 소문자로 시작하는 영문·숫자·-·_ 조합(50자 이하)이어야 합니다."
            )
        self._validate_tabs(command.tabs)
        grade = await self._grades.create_grade(command.code, command.name, command.tabs)
        await self._audit.write(
            actor_id=command.actor_id,
            action="grade.create",
            detail=f"grade={command.code}({command.name}) tabs={','.join(command.tabs) or '-'}",
        )
        return GradeResponse(grade=grade)

    async def update_grade(self, command: GradeUpdateCommand) -> GradeResponse:
        if command.code == PROTECTED_CODE and command.name is not None:
            raise GradeProtectedError("admin 역할의 이름은 변경할 수 없습니다.")
        if command.tabs is not None:
            self._validate_tabs(command.tabs)
        grade = await self._grades.update_grade(command.code, command.name, command.tabs)
        await self._audit.write(
            actor_id=command.actor_id,
            action="grade.update",
            detail=f"grade={command.code} name={command.name or '-'} "
            f"tabs={','.join(command.tabs) if command.tabs is not None else '-'}",
        )
        return GradeResponse(grade=grade)

    async def delete_grade(self, command: GradeDeleteCommand) -> None:
        if command.code == PROTECTED_CODE:
            raise GradeProtectedError("admin 역할은 삭제할 수 없습니다.")
        # 삭제 전 스냅샷 — 감사 로그에 회수 규모(member_count)를 남긴다.
        info = next(
            (g for g in await self._grades.list_grades() if g.code == command.code), None
        )
        await self._grades.delete_grade(command.code)
        await self._audit.write(
            actor_id=command.actor_id,
            action="grade.delete",
            detail=f"grade={command.code} revoked_members={info.member_count if info else 0}",
        )

    @staticmethod
    def _validate_tabs(tabs: tuple[str, ...]) -> None:
        unknown = [t for t in tabs if t not in TAB_KEYS]
        if unknown:
            raise GradeValidationError(f"등록되지 않은 탭 키입니다: {', '.join(unknown)}")
