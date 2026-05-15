"""
Memory Agent — 长期记忆管理（Redis + PostgreSQL）
"""
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.redis_session import get_session_manager, RedisSessionManager
from app.models import User, Conversation, Message, TravelRoute


class MemoryAgent:
    """管理用户长期记忆: 对话历史持久化、用户偏好学习"""

    def __init__(self):
        self._redis: Optional[RedisSessionManager] = None

    async def _get_redis(self) -> RedisSessionManager:
        if self._redis is None:
            self._redis = await get_session_manager()
        return self._redis

    # ── PostgreSQL 持久化 ──

    async def save_message(
        self, db: AsyncSession, session_id: str, role: str, content: str,
        user_id: Optional[int] = None,
    ):
        """保存消息到 PostgreSQL，自动设置对话标题为用户第一条输入"""
        conv = await self._get_or_create_conversation(db, session_id, user_id)
        # 用用户第一条消息作为对话标题
        if role == "user" and conv.title == "New Conversation":
            conv.title = content[:50]  # 截断到50字符
        msg = Message(conversation_id=conv.id, role=role, content=content)
        db.add(msg)
        await db.commit()

    async def save_route(
        self, db: AsyncSession, session_id: str, route_data: dict, map_image: str = ""
    ):
        """保存旅行路线"""
        conv = await self._get_or_create_conversation(db, session_id)
        route = TravelRoute(
            conversation_id=conv.id,
            session_id=session_id,
            route_json=route_data,
            map_image=map_image,
        )
        db.add(route)
        await db.commit()

    async def get_history(
        self, db: AsyncSession, session_id: str, limit: int = 50
    ) -> list[dict]:
        """获取会话历史消息"""
        conv = await self._get_or_create_conversation(db, session_id)
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = result.scalars().all()
        return [{"role": m.role, "content": m.content} for m in reversed(messages)]

    async def list_conversations(self, db: AsyncSession, user_id: int) -> list[dict]:
        """列出用户的所有对话"""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(50)
        )
        convs = result.scalars().all()
        return [{
            "id": c.id,
            "session_id": c.session_id,
            "title": c.title,
            "created_at": c.created_at.isoformat(),
        } for c in convs]

    # ── Redis 缓存 ──

    async def cache_context(self, session_id: str, role: str, content: str):
        """缓存消息到 Redis"""
        redis = await self._get_redis()
        await redis.add_message(session_id, role, content)

    async def get_cached_context(self, session_id: str) -> list[dict]:
        redis = await self._get_redis()
        return await redis.get_context(session_id)

    # ── 内部 ──

    async def _get_or_create_conversation(
        self, db: AsyncSession, session_id: str, user_id: Optional[int] = None
    ) -> Conversation:
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conv = result.scalar_one_or_none()
        if conv is None:
            conv = Conversation(session_id=session_id, user_id=user_id)
            db.add(conv)
            await db.commit()
            await db.refresh(conv)
        return conv


memory_agent = MemoryAgent()
