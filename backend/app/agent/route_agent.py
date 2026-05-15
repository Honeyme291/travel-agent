"""
Route Agent — 交通路线规划 + 地图生成
"""
import json

from langchain_core.messages import HumanMessage
from app.core.llm import get_llm
from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


async def _get_coords(city: str) -> str:
    """城市 → 坐标"""
    geo = await mcp_manager.call("amap-maps", "maps_geo", address=city, city=city[:2])
    try:
        data = json.loads(geo) if isinstance(geo, str) else geo
        if isinstance(data, dict):
            ret = data.get("return") or data.get("geocodes")
            if isinstance(ret, list) and ret:
                return ret[0].get("location", "")
    except Exception:
        pass
    return ""


async def _get_driving(origin_coords: str, dest_coords: str) -> str:
    return await mcp_manager.call(
        "amap-maps", "maps_direction_driving",
        origin=origin_coords, destination=dest_coords,
    )


def plan_route(origin: str, destination: str) -> dict:
    """
    规划两地之间的驾车路线

    返回: { driving, origin_coords, dest_coords }
    """
    o_coords = run_async(_get_coords(origin))
    d_coords = run_async(_get_coords(destination))

    result = {"origin_coords": o_coords, "dest_coords": d_coords}

    if o_coords and d_coords:
        driving = run_async(_get_driving(o_coords, d_coords))
        result["driving"] = driving

    return result


def generate_route_summary(route_data: dict) -> str:
    """LLM 生成路线摘要"""
    llm = get_llm()
    prompt = f"""根据以下路线数据，生成简洁的交通建议:

{json.dumps(route_data, ensure_ascii=False, indent=2)}

请说明: 距离、预计时间、推荐交通方式"""
    resp = llm.invoke([HumanMessage(content=prompt)])
    return resp.content
