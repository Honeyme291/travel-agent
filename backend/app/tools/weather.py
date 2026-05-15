"""
天气查询工具 — amap-maps / maps_weather
"""
import json

from langchain_classic.tools import Tool

from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


def create_weather_tool() -> Tool:
    """创建天气查询工具"""

    def sync_func(tool_input: str) -> str:
        from app.tools.base import parse_tool_input
        kwargs = parse_tool_input(tool_input)
        city = kwargs.get("city") or kwargs.get("location") or kwargs.get("query", "")

        city = city.replace("市", "").split(",")[0].split("，")[0].strip()

        async def _call():
            return await mcp_manager.call("amap-maps", "maps_weather", city=city)

        return run_async(_call())

    return Tool(
        name="gaode_weather",
        description=(
            "查询指定城市的天气预报，包括温度、天气状况、风力、湿度等。"
            "输入城市名即可，例如: '北京'。对每个目的地城市都应调用一次。"
        ),
        func=sync_func,
    )
