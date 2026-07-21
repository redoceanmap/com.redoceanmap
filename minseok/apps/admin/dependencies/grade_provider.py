from __future__ import annotations

from fastapi import Depends

from admin.app.ports.input.grade_use_case import GradeUseCase
from admin.app.ports.output.audit_log_port import AuditLogPort
from admin.app.use_cases.grade_interactor import GradeInteractor
from admin.dependencies.audit_provider import get_audit_log_port
from hub.app.ports.output.grade_policy_port import GradePolicyPort
from hub.dependencies.grade_policy_provider import get_grade_policy_port


def get_grade_use_case(
    grades: GradePolicyPort = Depends(get_grade_policy_port),
    audit: AuditLogPort = Depends(get_audit_log_port),
) -> GradeUseCase:
    return GradeInteractor(grades=grades, audit=audit)
