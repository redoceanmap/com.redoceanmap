from pydantic import BaseModel, Field


class PostmasterSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("이메일 발송 창구 (hub/email)", description="Postmaster's name")
    # 이메일 요청의 온톨로지 지시 합성과 위임

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 7,
                "name": "Postmaster",
            }
        }
    }


class PostmasterResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
