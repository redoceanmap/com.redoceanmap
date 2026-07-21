"""RBAC 4테이블 — roles / permissions / user_roles / role_permissions.

users를 소유한 auth 앱이 역할·권한 매핑도 소유한다(refresh_tokens FK 선례).
권한 검사는 core.security.require_permission이 매 요청 조인 조회로 수행한다.
"""
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class RoleOrm(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))


class PermissionOrm(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255))


class UserRoleOrm(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)


class RolePermissionOrm(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"), index=True)


class RoleTabOrm(Base):
    """역할(=등급)별 노출 탭 — 유저의 보이는 탭은 보유 역할들의 탭 합집합."""

    __tablename__ = "role_tabs"
    __table_args__ = (UniqueConstraint("role_id", "tab_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    tab_key: Mapped[str] = mapped_column(String(50))
