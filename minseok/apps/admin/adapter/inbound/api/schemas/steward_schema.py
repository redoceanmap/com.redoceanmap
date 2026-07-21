from pydantic import BaseModel


class StewardResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str


class StewardAccessResponseSchema(BaseModel):

    user_id: int
    permissions: list[str]
