from pydantic import BaseModel


class DatasetStatSchema(BaseModel):
    key: str
    name: str
    row_count: int
    latest_label: str | None


class DataSourceListResponseSchema(BaseModel):
    datasets: list[DatasetStatSchema]
