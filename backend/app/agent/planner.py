"""
Planner Agent — 意图识别 + 信息提取 + 任务规划
"""
from typing import TypedDict, Optional

from langchain_core.messages import HumanMessage
from app.core.llm import get_llm


class PlanResult(TypedDict):
    need_tools: bool
    tasks: list[str]
    extraction: dict


def plan(user_input: str, context: list[dict]) -> PlanResult:
    """
    分析用户意图，决定需要执行哪些任务。

    返回: { need_tools, tasks, extraction }
    """
    llm = get_llm()

    context_str = "\n".join(
        f"{m['role']}: {m['content'][:200]}" for m in context[-5:]
    )

    prompt = f"""你是一个旅行规划调度器。分析用户输入，决定需要执行哪些任务。

对话历史:
{context_str}

用户最新输入: {user_input}

请输出 JSON（不要 markdown 代码块）:
{{
  "need_tools": true/false,
  "tasks": ["weather", "train", "hotel", "fortune", "route", "image"],
  "extraction": {{
    "destination": "城市",
    "origin": "出发城市",
    "travel_days": 天数,
    "budget": 预算,
    "travel_date": "YYYY-MM-DD"
  }}
}}

规则:
- 问候/闲聊: need_tools=false, tasks=[]
- 有具体旅行需求: need_tools=true
- 问天气: tasks=["weather"]
- 问交通: tasks=["train"]
- 完整旅行规划: tasks=["weather","train","hotel","fortune"]"""

    import json
    try:
        resp = llm.invoke([HumanMessage(content=prompt)])
        content = resp.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content)
    except Exception:
        return {"need_tools": False, "tasks": [], "extraction": {}}
