from datetime import datetime

from pydantic import BaseModel


class MonthCountSchema(BaseModel):
    month: str
    count: int


class CategoryCountSchema(BaseModel):
    category: str
    count: int


class RecentRecommendationSchema(BaseModel):
    id: int
    trdar_code: int
    trdar_name: str
    district_name: str
    category: str
    created_at: datetime


class DashboardResponseSchema(BaseModel):
    member_total: int
    member_new_this_month: int
    area_count: int
    latest_quarter: str | None
    recommendation_total: int
    recommendation_today: int
    monthly: list[MonthCountSchema]
    top_categories: list[CategoryCountSchema]
    recent: list[RecentRecommendationSchema]
