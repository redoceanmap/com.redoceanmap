from pydantic import BaseModel, Field


class JudgeSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("메일 판단기", description="Judge's name")
    # 단서(유사 메일)를 종합해 일반 메일의 최종 판단을 내리는 핵심 추론 담당

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 9,
                "name": "메일 판단기",
            }
        }
    }


class JudgeResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
