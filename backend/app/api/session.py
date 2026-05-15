"""
会话管理 API
"""
from fastapi import APIRouter

from app.schemas.models import SessionClearRequest, SessionClearResponse
from app.services.travel_service import travel_service

router = APIRouter()


@router.post("/session/clear", response_model=SessionClearResponse)
async def clear_session(req: SessionClearRequest):
    """清除指定会话的聊天记录"""
    travel_service.clear_session(req.session_id)
    return SessionClearResponse(session_id=req.session_id)


@router.post("/session/new")
async def new_session():
    """生成新 session ID"""
    import uuid
    return {"session_id": str(uuid.uuid4())[:8]}
