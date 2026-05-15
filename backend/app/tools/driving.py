"""
自驾路线规划工具 — amap-maps / maps_direction_driving
"""
import json

from langchain_classic.tools import Tool

from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


def create_driving_tool() -> Tool:
    """创建自驾路线规划工具"""

    def sync_func(tool_input: str) -> str:
        from app.tools.base import parse_tool_input
        kwargs = parse_tool_input(tool_input)
        origin = kwargs.get("origin") or kwargs.get("from", "")
        destination = kwargs.get("destination") or kwargs.get("to", "")

        if not origin or not destination:
            return "需要提供起点(origin)和终点(destination)坐标"

        async def _call():
            return await mcp_manager.call(
                "amap-maps", "maps_direction_driving",
                origin=origin, destination=destination
            )

        return run_async(_call())

    return Tool(
        name="gaode_driving",
        description=(
            "自驾路线规划，获取两地之间的驾车距离、预计时间、路线详情。"
            "输入JSON: {\"origin\": \"经度,纬度\", \"destination\": \"经度,纬度\"}。"
            "注意: 需要先通过 gaode_geo 获取坐标。"
        ),
        func=sync_func,
    )
