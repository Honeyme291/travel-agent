"""
R1 深度分析工具 — 使用 DashScope 兼容的 LLM 进行深度旅行规划分析
"""
import json

from langchain.chat_models import init_chat_model
from langchain_classic.tools import Tool

from app.config.settings import settings


def create_r1_tool() -> Tool:
    """创建深度分析工具"""

    def sync_func(tool_input: str) -> str:
        inp = tool_input.strip()
        if inp.startswith("{"):
            try:
                kwargs = json.loads(inp)
            except json.JSONDecodeError:
                kwargs = {"problem": inp, "context": {}}
        else:
            kwargs = {"problem": inp, "context": {}}

        problem = kwargs.get("problem", "")
        context = kwargs.get("context", {})

        api_key = settings.DEEPSEEK_API_KEY
        if not api_key:
            return "深度分析不可用: 未配置 API Key"

        try:
            llm = init_chat_model(
                model="openai:qwen-plus",
                api_key=api_key,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=0.7,
            )

            prompt = f"""你是一个专业的旅行规划优化师。请对以下旅行规划问题进行深度分析和优化：

问题描述：{problem}

已收集的信息：
{json.dumps(context, ensure_ascii=False, indent=2) if context else '无额外上下文'}

你的任务：
1. **路线优化**：分析多段行程的最优顺序和连接方式
2. **时间安排**：每个目的地的合理停留时间
3. **预算分配**：根据各段行程的物价和景点密度分配预算
4. **风险评估**：识别天气、交通、时间等风险
5. **备选方案**：提供经济型、舒适型等不同方案

输出JSON格式（纯JSON，不要markdown代码块）：
{{
  "route_optimization": "路线优化建议",
  "time_arrangement": "时间安排建议",
  "budget_allocation": {{"城市名": 预算金额}},
  "risk_warnings": ["风险1", "风险2"],
  "alternative_plans": [{{
    "name": "方案名称",
    "description": "方案描述",
    "total_cost": 总费用,
    "pros": ["优点1"],
    "cons": ["缺点1"]
  }}],
  "final_recommendation": "最终建议"
}}"""

            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"深度分析暂时不可用: {str(e)}"

    return Tool(
        name="r1_analysis",
        description=(
            "深度旅行规划分析和优化工具。"
            "适用于多目的地路线优化、预算紧张场景、复杂约束条件（老人/儿童同行等）。"
            "输入JSON: {\"problem\": \"问题描述\", \"context\": {...上下文信息...}}。"
        ),
        func=sync_func,
    )
