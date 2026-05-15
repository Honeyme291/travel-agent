"""
地理编码工具 — amap-maps / maps_geo
"""
import json

from langchain_classic.tools import Tool

from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


def create_geo_tool() -> Tool:
    """创建地理编码工具"""

    def sync_func(tool_input: str) -> str:
        from app.tools.base import parse_tool_input
        kwargs = parse_tool_input(tool_input)
        address = kwargs.get("address") or kwargs.get("location") or kwargs.get("query", "")
        city = kwargs.get("city", "")

        async def _call():
            return await mcp_manager.call("amap-maps", "maps_geo", address=address, city=city)

        return run_async(_call())

    return Tool(
        name="gaode_geo",
        description=(
            "地理编码工具，将地址名称转换为经纬度坐标。"
            "输入JSON: {\"address\": \"北京市朝阳区\", \"city\": \"北京\"}。"
            "也可直接输入地址名称。"
        ),
        func=sync_func,
    )
