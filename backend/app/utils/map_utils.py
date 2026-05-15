"""
地图工具 — 高德静态地图、路线图生成
"""
import os
from urllib.parse import urlencode


AMAP_KEY = os.getenv("AMAP_KEY", "")


def generate_static_map(
    center: str,
    zoom: int = 12,
    size: str = "800*400",
    markers: list[str] = None,
    scale: int = 2,
) -> str:
    """
    生成高德静态地图 URL

    Args:
        center: 中心坐标 "lng,lat"
        zoom: 缩放级别
        size: 图片尺寸 "宽*高"
        markers: 标注点列表 ["lng,lat", ...]
        scale: 分辨率倍率

    Returns: 静态地图图片 URL
    """
    params = {
        "key": AMAP_KEY,
        "location": center,
        "zoom": zoom,
        "size": size,
        "scale": scale,
    }
    if markers:
        params["markers"] = ",".join(markers)

    return f"https://restapi.amap.com/v3/staticmap?{urlencode(params)}"


def generate_route_map_url(
    origin: str,
    destination: str,
    waypoints: list[str] = None,
) -> dict:
    """
    生成路线地图数据

    Args:
        origin: 起点坐标 "lng,lat"
        destination: 终点坐标 "lng,lat"
        waypoints: 途经点坐标列表

    Returns: { static_url, origin, destination, waypoints }
    """
    markers = [origin, destination]
    if waypoints:
        markers.extend(waypoints)

    # 计算中心点（简化: 取起点和终点中点）
    parts_o = origin.split(",")
    parts_d = destination.split(",")
    center_lng = (float(parts_o[0]) + float(parts_d[0])) / 2
    center_lat = (float(parts_o[1]) + float(parts_d[1])) / 2
    center = f"{center_lng},{center_lat}"

    static_url = generate_static_map(center=center, markers=markers)

    return {
        "static_url": static_url,
        "origin": origin,
        "destination": destination,
        "waypoints": waypoints or [],
        "center": center,
    }
