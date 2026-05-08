import re


WKT_POINT_PATTERN = re.compile(
    r"POINT\s*\(\s*(?P<lon>-?\d+\.?\d*)\s+(?P<lat>-?\d+\.?\d*)\s*\)",
    re.IGNORECASE,
)

def parse_point(wkt: str) -> tuple[float, float]:
    """
    Parses a WKT POINT string into a (longitude, latitude) tuple.
    Raises ValueError if the string is invalid or coordinates are out of bounds.
    """
    match = WKT_POINT_PATTERN.fullmatch(wkt.strip())
    
    if match is None:
        raise ValueError(f"Invalid WKT format: {wkt!r}")
    
    lon = float(match["lon"])
    lat = float(match["lat"])
    
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"Longitude out of range (-180 to 180): {lon}")
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"Latitude out of range (-90 to 90): {lat}")
        
    return lon, lat