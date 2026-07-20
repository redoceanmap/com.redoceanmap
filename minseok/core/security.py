"""JWT 검증 의존성 — 전 라우터 공용 인증 가드.

발급은 auth 스포크(인터랙터) 몫이고, 여기는 무상태 서명 검증만 한다.
스포크가 auth를 import하면 스타 토폴로지 위반이므로 순수 인프라(core)에 둔다.
"""
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from jose import JWTError, jwt

from core.config import DOCS_PASSWORD, DOCS_USER, JWT_SECRET

ALGORITHM = "HS256"

_bearer = HTTPBearer(auto_error=False)
_basic = HTTPBasic(auto_error=False)


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


def verify_docs_credentials(
    credentials: HTTPBasicCredentials | None = Depends(_basic),
) -> None:
    """API 문서 보호 가드 — 브라우저 기본 로그인창(HTTP Basic)으로 개발자만 통과시킨다."""
    valid = (
        credentials is not None
        and bool(DOCS_USER)
        and bool(DOCS_PASSWORD)
        and secrets.compare_digest(credentials.username, DOCS_USER)
        and secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    )
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="문서 접근 인증이 필요합니다.",
            headers={"WWW-Authenticate": "Basic"},
        )
