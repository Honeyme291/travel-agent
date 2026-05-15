"""
公交/地铁路线规划工具 — amap-maps / maps_direction_transit_integrated
"""
import json

from langchain_classic.tools import Tool

from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


def create_transit_tool() -> Tool:
    """创建公交路线规划工具"""

    def sync_func(tool_input: str) -> str:
        from app.tools.base import parse_tool_input
        kwargs = parse_tool_input(tool_input)
        origin = kwargs.get("origin", "")
        destination = kwargs.get("destination", "")
        city = kwargs.get("city", "")
        cityd = kwargs.get("cityd", city)

        if not origin or not destination:
            return "需要提供起点(origin)和终点(destination)坐标"

        async def _call():
            return await mcp_manager.call(
                "amap-maps", "maps_direction_transit_integrated",
                origin=origin, destination=destination,
                city=city, cityd=cityd
            )

        return run_async(_call())

    return Tool(
        name="gaode_transit",
        description=(
            "公交/地铁路线规划，获取两地之间的公共交通换乘方案。"
            "输入JSON: {\"origin\": \"起点坐标\", \"destination\": \"终点坐标\", \"city\": \"城市名\", \"cityd\": \"目的城市名\"}。"
        ),
        func=sync_func,
    )
