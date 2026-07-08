from pydantic import BaseModel, ConfigDict


class AreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trdar_code: int
    trdar_name: str
    trdar_div_code: str
    trdar_div_name: str
    x_coord: int
    y_coord: int
    lat: float
    lng: float
    district_code: int
    district_name: str
    adm_dong_code: int
    adm_dong_name: str
    area_size: int
    region: str
