from pydantic import BaseModel, Field


class CuratorSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("추천 기록 (recommendation)", description="Curator's name")
    # 추천 이력의 보관과 재조회

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 5,
                "name": "Curator",
            }
        }
    }


class CuratorResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
