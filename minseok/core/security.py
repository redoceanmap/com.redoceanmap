"""JWT 검증 의존성 — 전 라우터 공용 인증 가드.

발급은 auth 스포크(인터랙터) 몫이고, 여기는 무상태 서명 검증만 한다.
스포크가 auth를 import하면 스타 토폴로지 위반이므로 순수 인프라(core)에 둔다.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.config import JWT_SECRET

ALGORITHM = "HS256"

_bearer = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> int:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
