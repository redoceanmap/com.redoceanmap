from pydantic import BaseModel, Field


class VisionSchema(BaseModel):

    id: int = Field(0, description="Agent ID")
    name: str = Field("비전 처리 (vision)", description="Vision's name")
    # 이미지 비전 처리

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 11,
                "name": "Vision",
            }
        }
    }


class VisionResponseSchema(BaseModel):

    id: int
    name: str
    introduction: str


class VisionImageResponseSchema(BaseModel):

    filename: str
    contentType: str
    sizeBytes: int
    objectKey: str
    message: str
