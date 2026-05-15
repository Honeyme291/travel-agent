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
        url="https://mcp.api-inference.modelscope.net/42a6badeb9744b/mcp",
        description="高德地图服务 — 天气、地理编码、POI搜索、路线规划",
    ),
    "12306-mcp": MCPServerConfig(
        name="12306-mcp",
        url="https://mcp.api-inference.modelscope.net/c5a4e4a633514a/mcp",
        description="12306 火车票查询 — 站点代码、车票查询、中转查询",
    ),
    "Bazi-MCP": MCPServerConfig(
        name="Bazi-MCP",
        url="https://mcp.api-inference.modelscope.net/293453453eaf40/mcp",
        description="黄历/八字查询 — 黄历吉日、八字命理",
    ),
}
