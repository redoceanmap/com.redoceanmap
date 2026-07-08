from pydantic import BaseModel, Field


class PostmanSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("수신 메일함 (mail)", description="Postman's name")
    # 수신 메일의 영속화와 의미 검색

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 8,
                "name": "Postman",
            }
        }
    }


class PostmanResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
