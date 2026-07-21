"""등급 정책 협력 포트 — admin(소비)과 auth(구현: roles·role_tabs 소유)를 잇는다.

MemberDirectoryPort(회원·역할 부여/회수)와 별개인 등급 구성 전용 계약이다
(Directory/Record 분리 선례 — 포트 비대화 회피). 유저 개인의 노출 탭 조회는
auth 스포크 내부 관심사라 이 계약에 없다(GET /auth/tabs).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.grade_dto import GradeInfo


class GradePolicyPort(ABC):

    @abstractmethod
    async def list_grades(self) -> list[GradeInfo]:
        """전체 등급(역할)을 탭 구성·보유 회원 수와 함께 반환한다."""
        ...

    @abstractmethod
    async def create_grade(self, code: str, name: str, tabs: tuple[str, ...]) -> GradeInfo:
        """등급을 생성한다. code 중복이면 ValueError."""
        ...

    @abstractmethod
    async def update_grade(
        self, code: str, name: str | None, tabs: tuple[str, ...] | None
    ) -> GradeInfo:
        """이름·탭 구성을 갱신한다(None은 유지). 등급 부재면 ValueError."""
        ...

    @abstractmethod
    async def delete_grade(self, code: str) -> None:
        """등급을 삭제한다 — role_tabs·role_permissions·user_roles 동반 삭제. 부재면 ValueError."""
        ...
