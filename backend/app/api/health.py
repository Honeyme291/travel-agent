"""
健康检查 API — GET /api/health
"""
from fastapi import APIRouter

from app.config.settings import settings
from app.services.travel_service import travel_service

router = APIRouter()


@router.get("/health")
async def health_check():
    """返回服务和 MCP 服务器状态"""
    return {
        "status": "ok",
        "version": settings.VERSION,
        "mcp_servers": travel_service.get_server_status(),
    }
