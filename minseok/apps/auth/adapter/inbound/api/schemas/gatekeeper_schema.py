from pydantic import BaseModel, Field


class GatekeeperSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("인증 서비스 (auth)", description="Gatekeeper's name")
    # 인증/인가의 관문 — 로그인·토큰 검증

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Gatekeeper",
            }
        }
    }


class GatekeeperResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
