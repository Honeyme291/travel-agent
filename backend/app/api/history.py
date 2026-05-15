"""
历史会话 API — 当 PostgreSQL 不可用时优雅降级返回空列表
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.agent.memory_agent import memory_agent

router = APIRouter()


@router.get("/history/conversations")
async def list_conversations(
    user_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    """列出用户的对话列表"""
    if not user_id:
        raise HTTPException(400, "user_id required")
    try:
        convs = await memory_agent.list_conversations(db, user_id)
        return {"conversations": convs}
    except Exception as e:
        # PostgreSQL 不可用时降级为空列表
        return {"conversations": [], "note": f"Database unavailable: {str(e)[:100]}"}


@router.get("/history/messages")
async def get_messages(
    session_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """获取对话消息"""
    if not session_id:
        raise HTTPException(400, "session_id required")
    try:
        messages = await memory_agent.get_history(db, session_id, limit)
        return {"messages": messages}
    except Exception as e:
        return {"messages": [], "note": f"Database unavailable: {str(e)[:100]}"}


@router.delete("/history/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除对话"""
    from sqlalchemy import delete
    from app.models import Conversation
    try:
        await db.execute(
            delete(Conversation).where(Conversation.id == conversation_id)
        )
        await db.commit()
        return {"deleted": True}
    except Exception as e:
        raise HTTPException(503, f"Database error: {str(e)[:200]}")
