"""
工具列表 API — GET /api/tools
"""
from fastapi import APIRouter

from app.schemas.models import ToolsListResponse, ToolInfo
from app.services.travel_service import travel_service

router = APIRouter()


@router.get("/tools", response_model=ToolsListResponse)
async def list_tools():
    """获取所有可用工具及其描述"""
    names = travel_service.get_tool_names()
    # 尝试获取每个工具的描述
    from app.tools.registry import tool_registry
    all_tools = tool_registry.get_all()
    tool_map = {t.name: t.description for t in all_tools}

    result = [ToolInfo(name=n, description=tool_map.get(n, "")) for n in names]
    return ToolsListResponse(tools=result, count=len(result))
