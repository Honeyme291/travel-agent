"""
LangGraph Agent Workflow — 核心旅行规划编排

工作流:
  用户输入 → Planner(意图识别) → [条件路由]
    ├─ 问候/闲聊 → 直接回复
    └─ 旅行需求 → [并行执行]
         ├─ Weather Agent
         ├─ Route Agent
         ├─ Fortune Agent
         └─ Image Agent
              ↓
         综合回复生成
"""
from typing import TypedDict, List

from langchain_core.messages import HumanMessage, AIMessage
from app.core.llm import get_llm
from app.agent.planner import plan
from app.agent.weather_agent import run_weather_agent
from app.agent.route_agent import plan_route, generate_route_summary
from app.agent.image_agent import get_spot_card
from app.agent.fortune_agent import get_fortune, analyze_travel_fortune


class AgentState(TypedDict):
    session_id: str
    user_input: str
    context: list[dict]
    plan: dict
    weather: str
    route: dict
    fortune: str
    images: list
    final_answer: str


class TravelAgentWorkflow:
    """
    旅行规划 Agent 工作流

    使用方式:
        wf = TravelAgentWorkflow()
        result = await wf.run("我想去杭州玩3天", session_id="xxx")
    """

    async def run(self, user_input: str, session_id: str = "default", context: list[dict] = None) -> AgentState:
        state: AgentState = {
            "session_id": session_id,
            "user_input": user_input,
            "context": context or [],
            "plan": {},
            "weather": "",
            "route": {},
            "fortune": "",
            "images": [],
            "final_answer": "",
        }

        # Step 1: Planner 意图识别
        state["plan"] = plan(user_input, state["context"])

        if not state["plan"].get("need_tools"):
            # 简单对话，直接回复
            state["final_answer"] = self._simple_reply(user_input)
            return state

        # Step 2: 并行执行各项 Agent
        extraction = state["plan"].get("extraction", {})
        destination = extraction.get("destination", "")
        origin = extraction.get("origin", "")
        travel_date = extraction.get("travel_date", "")

        tasks = state["plan"].get("tasks", [])

        if "weather" in tasks and destination:
            state["weather"] = run_weather_agent(destination, travel_date)

        if "train" in tasks and origin and destination and travel_date:
            state["route"] = plan_route(origin, destination)

        if "fortune" in tasks and travel_date:
            fortune_raw = get_fortune(travel_date)
            state["fortune"] = analyze_travel_fortune(fortune_raw)

        if "image" in tasks and destination:
            state["images"] = [get_spot_card(destination)]

        # Step 3: 综合回复生成
        state["final_answer"] = self._generate_final_answer(state, extraction)

        return state

    def _simple_reply(self, user_input: str) -> str:
        try:
            llm = get_llm()
            prompt = f"""用户说: "{user_input}"

你是智慧旅行助手。请友好回复，简介你的功能:
- 旅游路线规划
- 天气查询
- 火车票查询
- 黄历吉日
- 酒店推荐"""
            resp = llm.invoke([HumanMessage(content=prompt)])
            return resp.content
        except Exception as e:
            return (
                f"您好！我是智慧旅行助手 🗺️\n\n"
                f"我可以帮您:\n"
                f"- 📍 规划旅游路线\n"
                f"- ☀️ 查询天气预报\n"
                f"- 🚆 查询火车票\n"
                f"- 🗓️ 查看黄历吉日\n"
                f"- 🏨 推荐酒店住宿\n\n"
                f"（AI 模型暂时不可用: {str(e)[:100]}，请稍后重试）"
            )

    def _generate_final_answer(self, state: AgentState, extraction: dict) -> str:
        import json
        try:
            llm = get_llm()
            prompt = f"""你是智慧旅行助手。根据以下信息生成完整的旅行规划建议:

用户需求: {state['user_input']}
提取信息: {json.dumps(extraction, ensure_ascii=False)}

天气分析:
{state.get('weather', '无')}

路线规划:
{json.dumps(state.get('route', {}), ensure_ascii=False, indent=2)}

黄历分析:
{state.get('fortune', '无')}

请生成结构化的旅行规划:
1. 行程概览
2. 天气与穿衣建议
3. 交通方式推荐
4. 景点推荐
5. 注意事项
6. 总结建议

用Markdown格式，简洁明了。"""
            resp = llm.invoke([HumanMessage(content=prompt)])
            return resp.content
        except Exception as e:
            # LLM 不可用时，返回原始收集到的信息
            parts = ["## 旅行规划结果\n"]
            if state.get("weather"):
                parts.append(f"### ☀️ 天气\n{state['weather'][:500]}")
            if state.get("route"):
                parts.append(f"### 🚗 路线\n```json\n{json.dumps(state['route'], ensure_ascii=False, indent=2)[:500]}\n```")
            if state.get("fortune"):
                parts.append(f"### 🗓️ 黄历\n{state['fortune'][:300]}")
            parts.append(f"\n> AI 总结暂时不可用: {str(e)[:100]}")
            return "\n\n".join(parts)


async def run_travel_agent(user_input: str, session_id: str = "default", context: list[dict] = None) -> str:
    """便捷入口 — 运行 Agent 并返回最终回复"""
    wf = TravelAgentWorkflow()
    state = await wf.run(user_input, session_id, context)
    return state["final_answer"]
