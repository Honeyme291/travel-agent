"""
旅行规划核心服务 — 编排 Agent + 预分析 + RAG 的完整流程
"""
import asyncio
import json
from typing import Dict, Any, Optional

from app.core.agent import run_agent
from app.core.rag import load_documents, build_retriever
from app.core.memory import memory_manager
from app.services.pre_analyzer import pre_analyze_query
from app.tools.mcp_manager import mcp_manager
from app.tools.registry import tool_registry


# 知名城市和景点列表，用于 LLM 不可用时的兜底提取
_KNOWN_CITIES = [
    "杭州", "西湖", "北京", "上海", "南京", "苏州", "成都", "重庆", "西安",
    "武汉", "广州", "深圳", "长沙", "厦门", "青岛", "大连", "桂林", "丽江",
    "三亚", "拉萨", "黄山", "泰山", "华山", "峨眉山", "九寨沟", "张家界",
    "故宫", "长城", "兵马俑", "外滩", "夫子庙", "鼓浪屿", "漓江", "阳朔",
]

def _fallback_extract_destination(query: str) -> str:
    """正则兜底：从用户输入中提取城市/景点名"""
    found = []
    for name in _KNOWN_CITIES:
        if name in query:
            found.append(name)
    return "、".join(found[:5])  # 最多5个，顿号分隔


class TravelService:
    """旅行规划服务 — 封装完整的请求处理流程"""

    def __init__(self):
        self._retrievers: Dict[str, object] = {}

    async def initialize(self) -> None:
        """初始化 MCP 连接"""
        await mcp_manager.initialize()

    async def chat(
        self,
        user_query: str,
        session_id: str = "default",
        uploaded_files: list = [],
    ) -> Dict[str, Any]:
        """处理聊天请求 — 完整流水线"""

        # 1. 构建 RAG 检索器（如有文件上传）
        retriever = None
        if uploaded_files:
            docs = load_documents(uploaded_files)
            retriever = build_retriever(docs)
            self._retrievers[session_id] = retriever

        # 2. 获取工具
        tools = tool_registry.get_all()

        # 3. 预分析
        pre_analysis = pre_analyze_query(user_query)
        scenario_type = pre_analysis.scenario_type
        needs_r1 = pre_analysis.needs_deep_analysis
        extraction = pre_analysis.extraction

        # 4. 构建 Agent 输入
        if needs_r1:
            enhanced_input = f"""用户查询: {user_query}

重要提示：系统检测到这是一个{'多目的地' if scenario_type == 'multi_destination' else '复杂'}场景。

请按以下顺序处理：
1. 首先调用 r1_analysis 进行深度路线规划和优化
2. 然后根据 R1 的建议，调用其他工具查询具体信息
3. 最后综合所有信息生成完整的旅行规划

已提取的信息：
- 目的地: {extraction.destination or '未知'}
- 出发地: {extraction.origin or '未知'}
- 旅行天数: {extraction.travel_days}
- 预算: {extraction.budget}元
- 出发日期: {extraction.travel_date or '未知'}
- 偏好: {extraction.preferences}"""
        else:
            enhanced_input = None

        # 5. 运行 Agent
        answer = run_agent(
            user_input=user_query,
            tools=tools,
            retriever=retriever,
            session_id=session_id,
            enhanced_input=enhanced_input,
        )

        # 如果 LLM 没提取到目的地，用正则兜底
        destination = extraction.destination if extraction else ""
        if not destination:
            destination = _fallback_extract_destination(user_query)

        return {
            "session_id": session_id,
            "answer": answer,
            "scenario_type": scenario_type,
            "tool_calls_count": len(tools),
            "destination": destination,
        }

    def clear_session(self, session_id: str) -> None:
        """清除会话记忆"""
        memory_manager.clear(session_id)
        self._retrievers.pop(session_id, None)

    def get_server_status(self) -> list:
        """获取 MCP 服务器连接状态"""
        return mcp_manager.available_servers

    @staticmethod
    def get_tool_names() -> list:
        """获取可用工具名列表"""
        return tool_registry.list_names()


travel_service = TravelService()
