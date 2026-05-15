"""
API 总路由 — 挂载所有子路由到 /api
"""
from fastapi import APIRouter

from app.api import chat, session, tools, health
from app.api import stream, history, auth

api_router = APIRouter(prefix="/api")
api_router.include_router(chat.router, tags=["Chat"])
api_router.include_router(session.router, tags=["Session"])
api_router.include_router(tools.router, tags=["Tools"])
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(stream.router, tags=["Streaming"])
api_router.include_router(history.router, tags=["History"])
api_router.include_router(auth.router, tags=["Auth"])
