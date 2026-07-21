from pydantic import BaseModel


class AreaOverviewSchema(BaseModel):
    trdar_code: int
    trdar_name: str
    gu_name: str
    dong_name: str
    store_count: int | None
    closure_rate: float | None
    monthly_sales: int | None


class AreaListResponseSchema(BaseModel):
    areas: list[AreaOverviewSchema]
