from abc import ABC, abstractmethod
from datetime import datetime

from auth.domain.entities.refresh_token_entity import RefreshToken


class RefreshTokenRepository(ABC):

    @abstractmethod
    async def create(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken: ...

    @abstractmethod
    async def find_by_token(self, token: str) -> RefreshToken | None: ...

    @abstractmethod
    async def delete(self, token: str) -> None: ...
