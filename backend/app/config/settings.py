"""
全局配置 — 从环境变量读取所有配置项
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME = "WeChat Travel Agent"
    VERSION = "3.0.0"

    # LLM
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    LLM_MODEL = "qwen-plus"
    LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_TEMPERATURE = 0.7

    # Embedding
    EMBEDDING_MODEL = "text-embedding-v3"

    # R1 / Deep Analysis
    DEEPSEEK_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    DEEPSEEK_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # RAG
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100
    RETRIEVER_K = 5

    # Agent
    MAX_ITERATIONS = 30

    # MCP
    MCP_REQUEST_TIMEOUT = 30

    # WeChat
    WECHAT_APPID = os.getenv("WECHAT_APPID", "")
    WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")
    WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", "")

    # External APIs
    AMAP_KEY = os.getenv("AMAP_KEY", "")
    QWEATHER_KEY = os.getenv("QWEATHER_KEY", "")
    UNSPLASH_KEY = os.getenv("UNSPLASH_KEY", "")
    PEXELS_KEY = os.getenv("PEXELS_KEY", "")

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    # Server
    HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    PORT = int(os.getenv("SERVER_PORT", "8000"))


settings = Settings()
