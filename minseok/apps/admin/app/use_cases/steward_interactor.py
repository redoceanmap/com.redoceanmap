from __future__ import annotations

import logging

from admin.app.dtos.steward_dto import (
    StewardAccessQuery,
    StewardAccessResponse,
    StewardQuery,
    StewardResponse,
)
from admin.app.ports.input.steward_use_case import StewardUseCase
from admin.app.ports.output.steward_record_port import StewardRecordPort
from hub.app.ports.output.member_directory_port import MemberDirectoryPort

logger = logging.getLogger(__name__)


class StewardInteractor(StewardUseCase):
    """어드민 콘솔 (admin) 대장 — 자기소개 + 접근 권한 판정. 담당: 운영 콘솔의 관문."""

    def __init__(self, record: StewardRecordPort, members: MemberDirectoryPort) -> None:
        self._record = record
        self._members = members

    async def introduce_myself(self, query: StewardQuery) -> StewardResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return StewardResponse(
            id=query.id,
            name=query.name,
            introduction=(
                "운영 콘솔을 담당합니다. GET /admin/me 접근 권한 판정, GET /admin/dashboard 운영 KPI, "
                "GET /admin/areas 상권 목록, GET /admin/members 회원·역할 관리(부여/회수), "
                "GET /admin/recommendations 추천 기록, GET /admin/data-sources 데이터셋 현황을 제공합니다. "
                "모든 데이터 엔드포인트는 RBAC permission 검사(403)를 통과해야 합니다."
            ),
        )

    async def my_access(self, query: StewardAccessQuery) -> StewardAccessResponse:
        permissions = await self._members.list_user_permissions(query.user_id)
        await self._record.record(
            subject="my_access", note=f"user={query.user_id} permissions={len(permissions)}"
        )
        return StewardAccessResponse(user_id=query.user_id, permissions=tuple(permissions))
