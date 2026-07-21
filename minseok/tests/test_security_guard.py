"""core/security 인증 가드 검증 — 미인증 401, 유효 토큰 통과, 변조 토큰 401, 정지/탈퇴 차단."""
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from core.config import JWT_SECRET
from core.database import get_db
from core.security import get_current_user_id

app = FastAPI()


@app.get("/protected", dependencies=[Depends(get_current_user_id)])
def protected():
    return {"ok": True}


class _StubResult:
    def __init__(self, row):
        self._row = row

    def first(self):
        return self._row


class _StubSession:
    """get_current_user_id의 users 상태 조회를 흉내낸다 — (suspended_at, deleted_at) 행."""

    def __init__(self, row):
        self._row = row

    async def execute(self, *_args, **_kwargs):
        return _StubResult(self._row)

    async def rollback(self):
        pass


def _override_db(row):
    async def _get_db():
        yield _StubSession(row)

    return _get_db


client = TestClient(app)

ACTIVE = (None, None)
NOW = datetime.now(timezone.utc)


def _token(user_id: int = 7, minutes: int = 60, secret: str = JWT_SECRET) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": str(user_id), "exp": expire}, secret, algorithm="HS256")


def _get(row=ACTIVE, token: str | None = None):
    app.dependency_overrides[get_db] = _override_db(row)
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        return client.get("/protected", headers=headers)
    finally:
        app.dependency_overrides.clear()


def test_토큰_없이_접근하면_401():
    assert _get().status_code == 401


def test_유효_토큰은_통과한다():
    assert _get(token=_token()).status_code == 200


def test_다른_키로_서명한_토큰은_401():
    assert _get(token=_token(secret="wrong-secret")).status_code == 401


def test_만료된_토큰은_401():
    assert _get(token=_token(minutes=-1)).status_code == 401


def test_정지된_계정은_기발급_토큰도_403():
    assert _get(row=(NOW, None), token=_token()).status_code == 403


def test_탈퇴한_계정은_401():
    assert _get(row=(None, NOW), token=_token()).status_code == 401


def test_존재하지_않는_유저는_401():
    assert _get(row=None, token=_token()).status_code == 401
