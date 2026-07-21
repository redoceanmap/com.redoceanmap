from datetime import datetime, timezone

from admin.app.dtos.audit_dto import AuditEntry, AuditListQuery
from admin.app.use_cases.audit_interactor import AuditInteractor


class _StubAudit:
    def __init__(self):
        self.requested_limit = None

    async def write(self, actor_id, action, detail):
        raise NotImplementedError

    async def list_recent(self, limit):
        self.requested_limit = limit
        return [
            AuditEntry(
                id=1,
                actor_id=3,
                action="role.grant",
                detail="user=4 role=admin",
                created_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
            )
        ]


async def test_감사_로그는_최신순_목록을_반환한다():
    stub = _StubAudit()
    result = await AuditInteractor(audit=stub).list_logs(AuditListQuery(limit=50))
    assert stub.requested_limit == 50
    assert result.items[0].action == "role.grant"


async def test_limit은_상한으로_보정한다():
    stub = _StubAudit()
    await AuditInteractor(audit=stub).list_logs(AuditListQuery(limit=99999))
    assert stub.requested_limit == 200