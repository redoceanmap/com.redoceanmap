from pydantic import BaseModel, Field


class SemanticAskSchema(BaseModel):

    prompt: str = Field(..., min_length=1, description="사용자 질문")

    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "성수동 카페 상권 요즘 어때?",
            }
        }
    }


class SemanticAskResponseSchema(BaseModel):

    destination: str
    entities: list[str]
    answer: str


class SemanticResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
