from pydantic import BaseModel


class TokenDto(BaseModel):
    access_token: str
    refresh_token: str
    name: str
    email: str
