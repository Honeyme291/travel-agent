"""
酒店搜索工具 — amap-maps / maps_text_search
"""
import json

from langchain_classic.tools import Tool

from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


def create_hotel_tool() -> Tool:
    """创建酒店搜索工具"""

    def sync_func(tool_input: str) -> str:
        from app.tools.base import parse_tool_input
        kwargs = parse_tool_input(tool_input)
        keywords = kwargs.get("keywords") or kwargs.get("keyword") or kwargs.get("query", "")
        city = kwargs.get("city") or kwargs.get("location", "")

        if keywords and "酒店" not in keywords and "民宿" not in keywords:
            keywords = f"{keywords} 酒店"

        async def _call():
            params = {"keywords": keywords}
            if city:
                params["city"] = city
            return await mcp_manager.call("amap-maps", "maps_text_search", **params)

        return run_async(_call())

    return Tool(
        name="gaode_hotel_search",
        description=(
            "搜索酒店和住宿信息。输入JSON: {\"keywords\": \"经济型酒店\", \"city\": \"北京\"}。"
            "也可直接输入城市名或酒店类型。"
        ),
        func=sync_func,
    )
