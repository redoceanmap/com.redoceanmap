from pydantic import BaseModel, Field


class DispatcherSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("자동화 창구 (hub/automation)", description="Dispatcher's name")
    # 자동화 단일 창구(/automation/*)의 관제

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 6,
                "name": "Dispatcher",
            }
        }
    }


class DispatcherResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str
