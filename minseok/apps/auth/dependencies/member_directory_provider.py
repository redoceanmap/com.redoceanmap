from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.adapter.outbound.gateways.member_directory_gateway import MemberDirectoryGateway
from auth.adapter.outbound.redis.refresh_token_redis_repository import (
    RefreshTokenRedisRepository,
)
from core.database import get_db
from core.redis import get_redis
from hub.app.ports.output.member_directory_port import MemberDirectoryPort


def get_member_directory_gateway(db: AsyncSession = Depends(get_db)) -> MemberDirectoryPort:
    """허브 MemberDirectoryPort의 auth 구현. main.py가 주입한다."""
    return MemberDirectoryGateway(
        session=db,
        refresh_repository=RefreshTokenRedisRepository(redis=get_redis()),
    )
