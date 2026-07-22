"""core/security 인증 가드 검증 — 미인증 401, 유효 토큰 통과, 변조 토큰 401, 정지/탈퇴 차단.

유효 토큰 케이스가 곧 교차 검증이다: 발급(개인키 RS256) → 가드(공개키만) 통과.
"""
import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from core.config import JWT_PUBLIC_KEY, jwt_private_key
from core.database import get_db
from core.security import get_current_user_id

# 공격 시나리오용 별도 키쌍 — 서버 키와 무관한 키로 서명한 토큰은 거부되어야 한다.
_OTHER_PRIVATE_PEM = (
    rsa.generate_private_key(public_exponent=65537, key_size=2048)
    .private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    .decode()
)

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


def _token(user_id: int = 7, minutes: int = 60, key: str | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": str(user_id), "exp": expire}, key or jwt_private_key(), algorithm="RS256")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


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
    assert _get(token=_token(key=_OTHER_PRIVATE_PEM)).status_code == 401


def test_만료된_토큰은_401():
    assert _get(token=_token(minutes=-1)).status_code == 401


def test_페이로드를_변조한_토큰은_401():
    header, _payload, signature = _token(user_id=7).split(".")
    forged = _b64url(json.dumps({"sub": "1", "exp": 9999999999}).encode())
    assert _get(token=f"{header}.{forged}.{signature}").status_code == 401


def test_alg_none_토큰은_401():
    header = _b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = _b64url(json.dumps({"sub": "7", "exp": 9999999999}).encode())
    assert _get(token=f"{header}.{payload}.").status_code == 401


def test_공개키를_비밀키_삼은_HS256_강제_토큰은_401():
    # 알고리즘 혼동 공격 — jose는 인코딩 단계에서 PEM을 HMAC 비밀로 쓰길 거부하므로,
    # 공격자가 하듯 HMAC-SHA256 서명을 직접 조립한다. 검증부 RS256 리터럴 고정이 막아야 한다.
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url(json.dumps({"sub": "7", "exp": 9999999999}).encode())
    signature = hmac.new(
        JWT_PUBLIC_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256
    ).digest()
    assert _get(token=f"{header}.{payload}.{_b64url(signature)}").status_code == 401


def test_정지된_계정은_기발급_토큰도_403():
    assert _get(row=(NOW, None), token=_token()).status_code == 403


def test_탈퇴한_계정은_401():
    assert _get(row=(None, NOW), token=_token()).status_code == 401


def test_존재하지_않는_유저는_401():
    assert _get(row=None, token=_token()).status_code == 401
