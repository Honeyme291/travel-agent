"""
LLM 初始化 — 创建 ChatOpenAI 实例（指向阿里云 DashScope / Qwen）
"""
from langchain_openai import ChatOpenAI
from app.config.settings import settings


def get_llm() -> ChatOpenAI:
    """返回配置好的 Qwen LLM 实例"""
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        openai_api_key=settings.DASHSCOPE_API_KEY,
        openai_api_base=settings.LLM_BASE_URL,
        temperature=settings.LLM_TEMPERATURE,
    )
