from pydantic import BaseModel, Field


class ConciergeSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("대화형 분석 창구 (chat)", description="Concierge's name")
    # 대화 의도 분류(phase0)와 최종 서술의 창구

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 2,
                "name": "Concierge",
            }
        }
    }


class ConciergeResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
