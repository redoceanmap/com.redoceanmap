from pydantic import BaseModel


class TokenDto(BaseModel):
    access_token: str
    name: str
    email: str
