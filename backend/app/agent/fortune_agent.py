"""
Fortune Agent — 黄历/八字查询 + 出行吉日分析
"""
from langchain_core.messages import HumanMessage
from app.core.llm import get_llm
from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


async def _query_fortune(date_str: str) -> str:
    return await mcp_manager.call(
        "Bazi-MCP", "getChineseCalendar",
        solarDatetime=f"{date_str}T12:00:00+08:00",
    )


def get_fortune(date_str: str) -> str:
    """查询指定日期的黄历"""
    return run_async(_query_fortune(date_str))


def analyze_travel_fortune(fortune_data: str) -> str:
    """LLM 分析黄历对出行的影响"""
    llm = get_llm()
    prompt = f"""根据以下黄历信息，分析该日期是否适合出行旅游:

黄历数据:
{fortune_data}

请简洁说明:
1. 宜/忌概述
2. 是否适合出行
3. 注意事项"""
    resp = llm.invoke([HumanMessage(content=prompt)])
    return resp.content
