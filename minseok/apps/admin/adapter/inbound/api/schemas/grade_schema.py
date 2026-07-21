from pydantic import BaseModel, Field


class GradeSchema(BaseModel):
    code: str
    name: str
    tabs: list[str]
    member_count: int


class GradeListResponseSchema(BaseModel):
    grades: list[GradeSchema]


class GradeCreateRequestSchema(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    tabs: list[str] = []


class GradeUpdateRequestSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    tabs: list[str] | None = None
