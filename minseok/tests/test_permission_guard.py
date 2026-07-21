"""core/security RBAC 권한 가드 검증 — 미인증 401, 권한 없음 403, 보유 시 통과."""
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from core.config import JWT_SECRET
from core.database import get_db
from core.security import require_permission

app = FastAPI()


@app.get("/admin-only", dependencies=[Depends(require_permission("members:read"))])
def admin_only():
    return {"ok": True}


class _StubResult:
    def __init__(self, row):
        self._row = row

    def first(self):
        return self._row


class _StubSession:
    """가드의 두 조회를 흉내낸다 — users 상태 조회는 정상 계정, 권한 조회는 granted 제어."""

    def __init__(self, granted: bool):
        self._granted = granted

    async def execute(self, query, *_args, **_kwargs):
        if "FROM users" in str(query):
            return _StubResult((None, None))  # (suspended_at, deleted_at) — 정상 계정
        return _StubResult((1,) if self._granted else None)

    async def rollback(self):
        pass


def _override_db(granted: bool):
    async def _get_db():
        yield _StubSession(granted)

    return _get_db


client = TestClient(app)


def _token(user_id: int = 7) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    return jwt.encode({"sub": str(user_id), "exp": expire}, JWT_SECRET, algorithm="HS256")


def test_토큰_없이_접근하면_401():
    app.dependency_overrides[get_db] = _override_db(granted=True)
    try:
        assert client.get("/admin-only").status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_권한이_없으면_403():
    app.dependency_overrides[get_db] = _override_db(granted=False)
    try:
        res = client.get("/admin-only", headers={"Authorization": f"Bearer {_token()}"})
        assert res.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_권한을_보유하면_통과한다():
    app.dependency_overrides[get_db] = _override_db(granted=True)
    try:
        res = client.get("/admin-only", headers={"Authorization": f"Bearer {_token()}"})
        assert res.status_code == 200
    finally:
        app.dependency_overrides.clear()
