from pydantic import BaseModel


class FaceMatchSchema(BaseModel):

    name: str
    confidence: float


class FaceRecognitionResponseSchema(BaseModel):

    filename: str
    matches: list[FaceMatchSchema]
