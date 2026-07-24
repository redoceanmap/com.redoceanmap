"""최초 admin 부여 CLI — python scripts/grant_admin.py <email>

RBAC 부트스트랩(admin을 만들 admin이 없음)을 해결하는 createsuperuser 격 스크립트.
멱등 — 이미 admin이면 안내만 하고 종료한다. 이후 부여/회수는 어드민 UI 몫.
"""
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]  # minseok
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps"))
from core.key.secret_manager import get_secret_manager  # noqa: E402

_secrets = get_secret_manager()


def main() -> int:
    if len(sys.argv) != 2:
        print("사용법: python scripts/grant_admin.py <email>")
        return 1
    email = sys.argv[1]

    url = _secrets.require("DATABASE_URL").replace("postgresql://", "postgresql+psycopg://")
    engine = create_engine(url)
    with engine.begin() as conn:
        user_id = conn.execute(
            text("SELECT id FROM users WHERE email = :email"), {"email": email}
        ).scalar()
        if user_id is None:
            print(f"유저를 찾을 수 없습니다: {email} (먼저 가입이 필요합니다)")
            return 1
        role_id = conn.execute(text("SELECT id FROM roles WHERE code = 'admin'")).scalar()
        if role_id is None:
            print("admin 역할이 없습니다 — alembic upgrade head 먼저 실행하세요.")
            return 1
        exists = conn.execute(
            text("SELECT 1 FROM user_roles WHERE user_id = :uid AND role_id = :rid"),
            {"uid": user_id, "rid": role_id},
        ).first()
        if exists:
            print(f"{email} (id={user_id})는 이미 admin입니다.")
            return 0
        conn.execute(
            text("INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"),
            {"uid": user_id, "rid": role_id},
        )
        print(f"{email} (id={user_id})에 admin 역할을 부여했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
