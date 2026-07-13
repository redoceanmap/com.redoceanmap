"""core/security 인증 가드 검증 — 미인증 401, 유효 토큰 통과, 변조 토큰 401."""
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from core.config import JWT_SECRET
from core.security import get_current_user_id

app = FastAPI()


@app.get("/protected", dependencies=[Depends(get_current_user_id)])
def protected():
    return {"ok": True}


client = TestClient(app)


def _token(user_id: int = 7, minutes: int = 60, secret: str = JWT_SECRET) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": str(user_id), "exp": expire}, secret, algorithm="HS256")


def test_토큰_없이_접근하면_401():
    assert client.get("/protected").status_code == 401


def test_유효_토큰은_통과한다():
    res = client.get("/protected", headers={"Authorization": f"Bearer {_token()}"})
    assert res.status_code == 200


def test_다른_키로_서명한_토큰은_401():
    forged = _token(secret="wrong-secret")
    res = client.get("/protected", headers={"Authorization": f"Bearer {forged}"})
    assert res.status_code == 401


def test_만료된_토큰은_401():
    expired = _token(minutes=-1)
    res = client.get("/protected", headers={"Authorization": f"Bearer {expired}"})
    assert res.status_code == 401
