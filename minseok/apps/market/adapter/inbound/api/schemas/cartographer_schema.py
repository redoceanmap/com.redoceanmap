from pydantic import BaseModel, Field


class CartographerSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("상권 데이터 조회 (market)", description="Cartographer's name")
    # 상권 데이터의 지도 제작자 — 전국 확장의 기반

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 3,
                "name": "Cartographer",
            }
        }
    }


class CartographerResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
