from pydantic import BaseModel, Field


class AnalystSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("주식 분석 (stock)", description="Analyst's name")
    # 지표+뉴스 결합 분석 — 백테스트로 검증되는 신호만

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 4,
                "name": "Analyst",
            }
        }
    }


class AnalystResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
