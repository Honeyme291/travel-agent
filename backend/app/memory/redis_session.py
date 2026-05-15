"""
Redis Session 管理 — 多轮对话上下文 + Agent 记忆缓存
"""
import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL = 7 * 24 * 3600  # 7 days


class RedisSessionManager:
    """管理用户 Session：缓存对话上下文、Agent 状态、最近消息"""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    @staticmethod
    def openid_to_session(openid: str) -> str:
        """OpenID → Session ID"""
        return hashlib.sha256(openid.encode()).hexdigest()[:32]

    async def get_session(self, session_id: str) -> dict:
        """获取用户 Session"""
        raw = await self.redis.get(f"session:{session_id}")
        if raw:
            return json.loads(raw)
        return {"session_id": session_id, "context": [], "last_active": datetime.now().isoformat()}

    async def save_session(self, session_id: str, data: dict):
        """保存用户 Session"""
        data["last_active"] = datetime.now().isoformat()
        await self.redis.setex(
            f"session:{session_id}",
            SESSION_TTL,
            json.dumps(data, ensure_ascii=False),
        )

    async def add_message(self, session_id: str, role: str, content: str):
        """追加一条消息到对话上下文"""
        sess = await self.get_session(session_id)
        sess.setdefault("context", []).append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat(),
        })
        # Keep last 50 messages
        if len(sess["context"]) > 50:
            sess["context"] = sess["context"][-50:]
        await self.save_session(session_id, sess)

    async def get_context(self, session_id: str) -> list[dict]:
        """获取最近对话上下文"""
        sess = await self.get_session(session_id)
        return sess.get("context", [])[-20:]

    async def clear_session(self, session_id: str):
        """清除 Session"""
        await self.redis.delete(f"session:{session_id}")

    async def set_state(self, session_id: str, key: str, value: Any):
        """设置 Agent 状态键值"""
        sess = await self.get_session(session_id)
        sess.setdefault("state", {})[key] = value
        await self.save_session(session_id, sess)

    async def get_state(self, session_id: str, key: str) -> Any:
        sess = await self.get_session(session_id)
        return sess.get("state", {}).get(key)


_session_manager: Optional[RedisSessionManager] = None


async def get_session_manager() -> RedisSessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = RedisSessionManager()
        await _session_manager.connect()
    return _session_manager
