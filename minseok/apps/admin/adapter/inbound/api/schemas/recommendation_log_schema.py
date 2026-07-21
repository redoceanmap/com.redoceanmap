from datetime import datetime

from pydantic import BaseModel


class RecommendationLogSchema(BaseModel):
    id: int
    trdar_name: str
    district_name: str
    category: str
    reason: str
    created_at: datetime


class RecommendationLogResponseSchema(BaseModel):
    total: int
    today: int
    items: list[RecommendationLogSchema]
