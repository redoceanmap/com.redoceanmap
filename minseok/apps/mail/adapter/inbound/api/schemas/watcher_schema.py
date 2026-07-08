from pydantic import BaseModel, Field


class WatcherSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("수신 분류기", description="Watcher's name")
    # 수신 메일을 관찰·기록하고 1차 분류(트리아지)하는 관문

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 10,
                "name": "수신 분류기",
            }
        }
    }


class WatcherResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str


class ScreenRequestSchema(BaseModel):

    text: str = Field(..., description="유해성 검사 대상 텍스트")


class ScreenResponseSchema(BaseModel):

    isAbusive: bool
    categories: list[str]
    scores: dict[str, float]
