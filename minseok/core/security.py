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

from core.config import DOCS_PASSWORD, DOCS_USER, JWT_PUBLIC_KEY
from core.database import get_db

_bearer = HTTPBearer(auto_error=False)
_basic = HTTPBasic(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> int:
    """JWT 서명 검증 + 계정 상태 검사 — 정지/탈퇴는 기발급 토큰도 즉시 차단한다.

    매 요청 users PK 조회 1회가 비용이지만, 정지가 액세스 토큰 수명(60분)만큼
    지연되는 것을 막는다(운영 결정 2026-07-21). 원시 SQL인 이유는 core가
    apps ORM을 import할 수 없어서다(스타 토폴로지).
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # 허용 알고리즘은 RS256 리터럴 고정 — env·설정으로 빼지 않는다(알고리즘 혼동 공격 방지).
        payload = jwt.decode(credentials.credentials, JWT_PUBLIC_KEY, algorithms=["RS256"])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    row = (
        await db.execute(
            text("SELECT suspended_at, deleted_at FROM users WHERE id = :uid"),
            {"uid": user_id},
        )
    ).first()
    if row is None or row[1] is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 계정입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if row[0] is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="정지된 계정입니다. 관리자에게 문의해 주세요.",
        )
    # 가드 SELECT가 연 트랜잭션을 즉시 닫아 커넥션을 반환한다 —
    # 이 세션을 재사용하는 긴 응답(예: chat SSE) 동안 풀 점유를 막는다.
    await db.rollback()
    return user_id


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
        granted = found.first() is not None
        await db.rollback()  # 권한 조회 트랜잭션도 즉시 종료(가드와 동일 사유)
        if not granted:
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
