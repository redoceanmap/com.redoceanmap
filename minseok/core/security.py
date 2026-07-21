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
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import DOCS_PASSWORD, DOCS_USER, JWT_SECRET
from core.database import get_db

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


def require_permission(code: str):
    """RBAC 권한 가드 팩토리 — 해당 permission 코드 미보유 시 403.

    JWT 클레임이 아니라 매 요청 DB 조회다 — 역할 회수가 즉시 반영된다(재로그인 불필요).
    core는 apps ORM을 import할 수 없으므로(스타 토폴로지) 원시 SQL로 조회한다.
    """

    async def _dep(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
    ) -> int:
        found = await db.execute(
            text(
                "SELECT 1 FROM user_roles ur "
                "JOIN role_permissions rp ON rp.role_id = ur.role_id "
                "JOIN permissions p ON p.id = rp.permission_id "
                "WHERE ur.user_id = :uid AND p.code = :code LIMIT 1"
            ),
            {"uid": user_id, "code": code},
        )
        if found.first() is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")
        return user_id

    return _dep


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
