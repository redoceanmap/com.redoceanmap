from __future__ import annotations

from fastapi import Depends

from admin.app.ports.input.member_use_case import MemberUseCase
from admin.app.ports.output.audit_log_port import AuditLogPort
from admin.app.use_cases.member_interactor import MemberInteractor
from admin.dependencies.audit_provider import get_audit_log_port
from hub.app.ports.output.member_directory_port import MemberDirectoryPort
from hub.dependencies.member_directory_provider import get_member_directory_port


def get_member_use_case(
    members: MemberDirectoryPort = Depends(get_member_directory_port),
    audit: AuditLogPort = Depends(get_audit_log_port),
) -> MemberUseCase:
    return MemberInteractor(members=members, audit=audit)
