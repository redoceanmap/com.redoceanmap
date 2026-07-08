from datetime import datetime

from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    id: int
    conversation_id: int | None
    trdar_code: int
    trdar_name: str
    district_name: str
    category: str
    reason: str
    lat: float
    lng: float
    created_at: datetime

    model_config = {"from_attributes": True}
