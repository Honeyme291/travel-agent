"""
POI 搜索工具 — amap-maps / maps_text_search
"""
import json

from langchain_classic.tools import Tool

from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


def create_poi_tool() -> Tool:
    """创建 POI 兴趣点搜索工具"""

    def sync_func(tool_input: str) -> str:
        from app.tools.base import parse_tool_input
        kwargs = parse_tool_input(tool_input)
        keywords = kwargs.get("keywords") or kwargs.get("keyword") or kwargs.get("query", "")
        city = kwargs.get("city") or kwargs.get("location", "")

        async def _call():
            params = {"keywords": keywords}
            if city:
                params["city"] = city
            return await mcp_manager.call("amap-maps", "maps_text_search", **params)

        return run_async(_call())

    return Tool(
        name="gaode_poi_search",
        description=(
            "搜索POI兴趣点，包括景点、餐厅、商场等。"
            "输入JSON: {\"keywords\": \"搜索关键词\", \"city\": \"城市名\"}。"
            "也可直接输入关键词进行搜索。"
        ),
        func=sync_func,
    )
