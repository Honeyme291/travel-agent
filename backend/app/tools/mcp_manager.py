"""
MCP 连接管理器 — 基于 MCP SDK streamable HTTP
"""
import json
import asyncio
from typing import Dict

from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

from app.config.mcp_servers import MCP_SERVERS, MCPServerConfig


class MCPManager:
    """管理与多个 MCP 服务器的连接和工具调用"""

    def __init__(self):
        self._servers: Dict[str, dict] = {}

    async def initialize(self) -> None:
        """逐个连接所有已配置的 MCP 服务器（顺序连接，避免 TaskGroup 问题）"""
        for name, config in MCP_SERVERS.items():
            await self._connect_server(name, config)

    async def _connect_server(self, name: str, config: MCPServerConfig) -> None:
        """连接单个 MCP 服务器（带超时和重试）"""
        for attempt in range(2):
            try:
                tools = await asyncio.wait_for(
                    self._list_tools(config.url),
                    timeout=15.0,
                )
                self._servers[name] = {
                    "config": config,
                    "tools": {t["name"]: t for t in tools},
                    "connected": True,
                }
                print(f"[MCP] {name} connected — {len(tools)} tools")
                return
            except asyncio.TimeoutError:
                print(f"[MCP] {name} timed out (attempt {attempt + 1})")
            except Exception as e:
                print(f"[MCP] {name} attempt {attempt + 1} failed: {type(e).__name__}")

        # 所有重试失败
        self._servers[name] = {
            "config": config,
            "tools": {},
            "connected": False,
        }
        print(f"[MCP] {name} unavailable — tools using this server will return errors")

    async def call(self, server_name: str, tool_name: str, **kwargs) -> str:
        """调用指定 MCP 服务器上的工具"""
        server = self._servers.get(server_name)
        if not server or not server.get("connected"):
            return json.dumps({
                "error": f"Server '{server_name}' unavailable"
            }, ensure_ascii=False)

        try:
            async with streamablehttp_client(server["config"].url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=kwargs)
                    return self._serialize(result)
        except Exception as e:
            return json.dumps({
                "error": str(e), "server": server_name, "tool": tool_name
            }, ensure_ascii=False)

    @property
    def available_servers(self) -> list:
        return [n for n, s in self._servers.items() if s.get("connected")]

    async def _list_tools(self, url: str) -> list:
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return [{
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": getattr(t, "inputSchema", {}),
                } for t in result.tools]

    @staticmethod
    def _serialize(result) -> str:
        if hasattr(result, "content") and result.content:
            parts = []
            for c in result.content:
                if hasattr(c, "text"):
                    parts.append(c.text)
                elif isinstance(c, dict):
                    parts.append(json.dumps(c, ensure_ascii=False))
                else:
                    parts.append(str(c))
            return "\n".join(parts)
        return json.dumps({"raw": str(result)}, ensure_ascii=False)


mcp_manager = MCPManager()
