"""
MCP 服务器配置 — 所有第三方 MCP 服务的 URL 和元信息
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class MCPServerConfig:
    name: str
    url: str
    description: str


# 真实 MCP 服务器列表
MCP_SERVERS: Dict[str, MCPServerConfig] = {
    "amap-maps": MCPServerConfig(
        name="amap-maps",
        url="",
        description="高德地图服务 — 天气、地理编码、POI搜索、路线规划",
    ),
    "12306-mcp": MCPServerConfig(
        name="12306-mcp",
        url="",
        description="12306 火车票查询 — 站点代码、车票查询、中转查询",
    ),
    "Bazi-MCP": MCPServerConfig(
        name="Bazi-MCP",
        url="",
        description="黄历/八字查询 — 黄历吉日、八字命理",
    ),
}
