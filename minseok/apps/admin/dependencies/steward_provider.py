from __future__ import annotations

from fastapi import Depends

from admin.adapter.outbound.log_steward_record_adapter import LogStewardRecordAdapter
from admin.app.ports.input.steward_use_case import StewardUseCase
from admin.app.use_cases.steward_interactor import StewardInteractor
from hub.app.ports.output.member_directory_port import MemberDirectoryPort
from hub.dependencies.member_directory_provider import get_member_directory_port


def get_steward_use_case(
    members: MemberDirectoryPort = Depends(get_member_directory_port),
) -> StewardUseCase:
    return StewardInteractor(record=LogStewardRecordAdapter(), members=members)
