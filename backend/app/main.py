"""
FastAPI 应用入口 — WeChat Travel Agent
"""
import asyncio
import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.wechat import router as wechat_router
from app.config.settings import settings
from app.services.travel_service import travel_service
from app.memory.redis_session import get_session_manager
from app.models.database import engine, Base

warnings.filterwarnings("ignore", category=DeprecationWarning)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期 — 启动时初始化所有连接"""
    # MCP 服务器连接
    await travel_service.initialize()

    # Redis 连接
    try:
        redis_sess = await get_session_manager()
        print(f"[Redis] Connected")
    except Exception as e:
        print(f"[Redis] Not available (running without cache): {e}")

    # PostgreSQL 建表
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f"[PostgreSQL] Tables ready")
    except Exception as e:
        print(f"[PostgreSQL] Not available (running without DB): {e}")

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes: /api/*
app.include_router(api_router)

# WeChat callback: /wechat/* (must be direct, not under /api)
app.include_router(wechat_router)
