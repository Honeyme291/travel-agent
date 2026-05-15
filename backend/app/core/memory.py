"""
对话记忆 — 基于 LangChain ConversationBufferMemory 的多会话管理
"""
from typing import Dict

from langchain_classic.memory import ConversationBufferMemory


class MemoryManager:
    """管理多个会话的对话记忆"""

    def __init__(self):
        self._memories: Dict[str, ConversationBufferMemory] = {}

    def get_or_create(self, session_id: str) -> ConversationBufferMemory:
        """获取或创建指定 session 的记忆"""
        if session_id not in self._memories:
            self._memories[session_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                output_key="output",
            )
        return self._memories[session_id]

    def clear(self, session_id: str) -> None:
        """清除指定 session 的记忆"""
        if session_id in self._memories:
            del self._memories[session_id]


memory_manager = MemoryManager()
