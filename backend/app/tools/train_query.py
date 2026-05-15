"""
火车票查询工具 — 12306 MCP
"""
import json
from datetime import datetime

from langchain_classic.tools import Tool

from app.tools.mcp_manager import mcp_manager


async def _get_station_code(city: str) -> str | None:
    """获取城市的主火车站代码"""
    result = await mcp_manager.call("12306-mcp", "get-stations-code-in-city", city=city)
    if "error" in str(result).lower():
        return None

    try:
        data = json.loads(result) if isinstance(result, str) else result
    except json.JSONDecodeError:
        return None

    if isinstance(data, list) and data:
        for station in data:
            name = station.get("station_name", "")
            if name == city or city in name:
                return station.get("station_code") or station.get("code")
        return data[0].get("station_code") or data[0].get("code")
    return None


async def _query_train(origin: str, destination: str, date: str) -> str:
    """查询火车票：先获取站点代码，再查询车票 + 自驾路线"""
    today = datetime.now()

    # 修正日期年份
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        if dt.year < today.year:
            date = date.replace(str(dt.year), str(today.year))
    except ValueError:
        pass

    from_code = await _get_station_code(origin)
    to_code = await _get_station_code(destination)

    combined = {}

    # 查询火车票
    if from_code and to_code:
        train_result = await mcp_manager.call(
            "12306-mcp", "get-tickets",
            fromStation=from_code, toStation=to_code, date=date
        )
        if train_result:
            combined["train"] = train_result

    # 自动附带自驾路线
    try:
        origin_geo = await mcp_manager.call("amap-maps", "maps_geo", address=origin, city=origin[:2])
        dest_geo = await mcp_manager.call("amap-maps", "maps_geo", address=destination, city=destination[:2])

        origin_coords = _extract_coords(origin_geo)
        dest_coords = _extract_coords(dest_geo)

        if origin_coords and dest_coords:
            driving = await mcp_manager.call(
                "amap-maps", "maps_direction_driving",
                origin=origin_coords, destination=dest_coords
            )
            if driving:
                combined["driving"] = driving
    except Exception:
        pass

    if combined:
        return json.dumps(combined, ensure_ascii=False)
    return "交通查询失败"


def _extract_coords(geo_result: str) -> str | None:
    """从地理编码结果中提取坐标"""
    try:
        data = json.loads(geo_result) if isinstance(geo_result, str) else geo_result
        if isinstance(data, dict):
            ret = data.get("return") or data.get("geocodes")
            if isinstance(ret, list) and ret:
                return ret[0].get("location")
        if isinstance(data, list) and data:
            return data[0].get("location")
    except (json.JSONDecodeError, IndexError, KeyError):
        pass
    return None


def create_train_query_tool() -> Tool:
    """创建火车票查询工具"""
    from app.tools.base import run_async, parse_tool_input
    import re

    def sync_func(tool_input: str) -> str:
        kwargs = parse_tool_input(tool_input)
        origin = kwargs.get("origin") or kwargs.get("from") or kwargs.get("fromStation") or kwargs.get("query", "")
        destination = kwargs.get("destination") or kwargs.get("to") or kwargs.get("toStation", "")
        date = kwargs.get("date", "")

        if (not origin or not destination) and kwargs.get("query"):
            q = kwargs["query"]
            m = re.search(r"从\s*(\S+?)\s*到\s*(\S+)", q)
            if m:
                origin = origin or m.group(1)
                destination = destination or m.group(2)
            m2 = re.search(r"(\d{4}-\d{2}-\d{2})", q)
            if m2:
                date = date or m2.group(1)

        if not origin or not destination:
            return "请提供出发城市(origin)和到达城市(destination)，例如: {\"origin\": \"北京\", \"destination\": \"上海\", \"date\": \"2026-05-20\"}"

        return run_async(_query_train(origin, destination, date))

    return Tool(
        name="train_query",
        description=(
            "查询火车票信息，支持查询两个城市之间的火车班次、时间、票价。"
            "输入JSON: {\"origin\": \"出发城市\", \"destination\": \"到达城市\", \"date\": \"YYYY-MM-DD\"}。"
            "该工具会自动获取站点代码并查询车票，同时附带自驾路线信息。"
        ),
        func=sync_func,
    )
