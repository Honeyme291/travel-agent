"""
黄历查询工具 — Bazi-MCP / getChineseCalendar
"""
import json

from langchain_classic.tools import Tool

from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


def create_lucky_day_tool() -> Tool:
    """创建黄历查询工具"""

    def sync_func(tool_input: str) -> str:
        from app.tools.base import parse_tool_input
        kwargs = parse_tool_input(tool_input)
        date_val = kwargs.get("date") or kwargs.get("solarDatetime") or kwargs.get("query", "") or str(tool_input).strip()

        date_val = date_val.strip()
        if "T" not in date_val:
            date_val = f"{date_val}T12:00:00+08:00"

        async def _call():
            return await mcp_manager.call(
                "Bazi-MCP", "getChineseCalendar",
                solarDatetime=date_val
            )

        return run_async(_call())

    return Tool(
        name="lucky_day",
        description=(
            "查询指定日期的黄历信息，包括农历日期、宜忌、冲煞等。"
            "输入日期字符串，例如: '2026-01-15'。用于选择出行吉日。"
        ),
        func=sync_func,
    )
