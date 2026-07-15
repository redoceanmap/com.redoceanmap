from pydantic import BaseModel, Field


class GeminiAnswerSchema(BaseModel):

    prompt: str = Field(..., min_length=1, description="Gemini에 보낼 질문/지시 텍스트")

    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "강남역 근처에서 카페 창업할 때 유의할 점을 알려줘",
            }
        }
    }


class GeminiAnswerResponseSchema(BaseModel):

    answer: str
    model: str


class GeminiResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
