from datetime import datetime

from pydantic import BaseModel


class MemberSchema(BaseModel):
    id: int
    email: str
    name: str
    joined_at: datetime | None
    marketing_agreed: bool
    roles: list[str]


class MemberListResponseSchema(BaseModel):
    total: int
    items: list[MemberSchema]


class RoleSchema(BaseModel):
    code: str
    name: str
    permissions: list[str]


class RoleListResponseSchema(BaseModel):
    roles: list[RoleSchema]


class RoleGrantRequestSchema(BaseModel):
    role_code: str
