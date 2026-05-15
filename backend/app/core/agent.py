"""
ReAct Agent — 基于 LangChain create_react_agent 的旅行规划 Agent
"""
from datetime import datetime

from typing import List, Optional



from langchain_classic.agents import create_react_agent, AgentExecutor

from langchain_classic.tools.retriever import create_retriever_tool


from langchain_core.prompts import PromptTemplate


from app.config.settings import settings
from app.core.llm import get_llm
from app.core.memory import memory_manager
from app.tools.registry import tool_registry


def _build_prompt() -> PromptTemplate:
    """构建 ReAct 提示词模板"""
    today = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().year

    instructions = f"""你是一个专业的旅游规划助手。当前日期是{today}。

**判断用户意图：**
- 如果用户只是打招呼（如"你好"）、问功能、或闲聊，直接友好回复，无需调用任何工具。
- 如果用户有具体旅行需求（提供了目的地、时间等信息），再按照以下规划流程操作。

**旅行规划流程（仅当用户有具体旅行需求时执行）：**

1. **交通信息**：
   - 调用 train_query 查询火车票
   - 长途（>800km）可提示航班

2. **天气预报**：
   - 对每个目的地调用 gaode_weather 查询天气

3. **住宿推荐**：
   - 调用 gaode_hotel_search 搜索酒店

4. **黄历吉日**：
   - 调用 lucky_day 查询出发日期的黄历信息

5. **复杂行程优化**：
   - 多城市或预算紧张的行程，调用 r1_analysis 深度分析

**重要规则：**
- 年份使用{current_year}
- 每个工具可以对不同参数多次调用
- 用中文回答，提供详尽的行程规划
"""

    template = """
{instructions}

TOOLS:
------
You have access to the following tools:
{tools}

To use a tool, use this EXACT format:

Thought: Do I need to use a tool? Yes
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

When you have a response, use:

Thought: Do I need to use a tool? No
Final Answer: [your response here]

CRITICAL RULES:
1. For greetings or general questions with NO travel details, reply directly — NO tools needed
2. For travel planning with destination/date details, call relevant tools: train_query, gaode_weather, gaode_hotel_search, lucky_day
3. You CAN call the same tool multiple times with DIFFERENT parameters
4. NEVER call the same tool with the SAME parameters twice
5. Use Chinese to respond to users

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}"""

    base = PromptTemplate.from_template(template)
    return base.partial(instructions=instructions)


def create_agent(
    tools: list,
    retriever: Optional[object] = None,
    session_id: str = "default",
):
    """创建并返回 AgentExecutor"""
    # 添加 RAG 检索工具（如果有文档）
    all_tools = list(tools)
    if retriever is not None:
        rag_tool = create_retriever_tool(
            retriever=retriever,
            name="rag_search",
            description="用于查询旅游攻略、景点信息、美食推荐等。输入城市名或景点名。"
        )
        all_tools.insert(0, rag_tool)

    llm = get_llm()
    prompt = _build_prompt()
    agent = create_react_agent(llm, all_tools, prompt)
    memory = memory_manager.get_or_create(session_id)

    return AgentExecutor(
        agent=agent,
        tools=all_tools,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=settings.MAX_ITERATIONS,
    )


def run_agent(
    user_input: str,
    tools: list,
    retriever: Optional[object] = None,
    session_id: str = "default",
    enhanced_input: Optional[str] = None,
) -> str:
    """执行 Agent 并返回结果"""
    executor = create_agent(tools, retriever, session_id)
    result = executor.invoke(
        {"input": enhanced_input or user_input},
        config={}
    )
    return result.get("output", "抱歉，无法生成回答。")
