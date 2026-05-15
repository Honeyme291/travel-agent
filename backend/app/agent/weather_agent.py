"""
Weather Agent — 天气查询 + 分析建议
"""
import json

from langchain_core.messages import HumanMessage
from app.core.llm import get_llm
from app.tools.mcp_manager import mcp_manager
from app.tools.base import run_async


async def query_weather(city: str) -> str:
    """查询城市天气"""
    result = await mcp_manager.call("amap-maps", "maps_weather", city=city)
    return result


async def analyze_weather(weather_data: str, travel_date: str) -> str:
    """LLM 分析天气对旅行的影响"""
    llm = get_llm()
    prompt = f"""根据以下天气数据，分析对旅行的影响和建议:

天气数据:
{weather_data}

旅行日期: {travel_date}

请简要说明:
1. 天气概况
2. 穿衣建议
3. 出行注意事项"""
    resp = llm.invoke([HumanMessage(content=prompt)])
    return resp.content


def run_weather_agent(city: str, travel_date: str = "") -> str:
    """同步入口 — 查询天气并返回分析"""
    weather = run_async(query_weather(city))
    if travel_date:
        return run_async(analyze_weather(weather, travel_date))
    return weather
