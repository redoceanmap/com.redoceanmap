from pyproj import Transformer

_transformer = Transformer.from_crs("EPSG:5174", "EPSG:4326", always_xy=True)


def tm_to_wgs84(x: int, y: int) -> tuple[float, float]:
    """EPSG:5174 (Korea Central Belt TM) → WGS84 (lng, lat)"""
    lng, lat = _transformer.transform(x, y)
    return round(lat, 6), round(lng, 6)
