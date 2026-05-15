"""
MCP Tool 基类和异步桥接工具
"""
import asyncio
from dataclasses import dataclass, field

import nest_asyncio

# 允许事件循环嵌套 — 使得在 FastAPI async handler 中可以同步调用 async MCP 方法
nest_asyncio.apply()


@dataclass
class ToolDefinition:
    """单个工具的定义"""
    name: str                           # Agent 可调用的工具名
    description: str                    # 给 LLM 的工具描述
    server_name: str                    # 目标 MCP 服务器名
    mcp_tool_name: str                  # 远程 MCP 工具名
    parameter_map: dict = field(default_factory=dict)  # 参数名映射


def run_async(coro):
    """
    在同步函数中安全地运行 async 协程。
    兼容三种场景：
      - 没有事件循环
      - 有事件循环但未运行
      - 有事件循环且正在运行（FastAPI / uvicorn）
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    if loop.is_running():
        # nest_asyncio 已 apply，可以直接嵌套执行
        return loop.run_until_complete(coro)
    else:
        return loop.run_until_complete(coro)


def parse_tool_input(tool_input: str) -> dict:
    """
    鲁棒地解析 LangChain Agent 工具输入。
    Agent 可能在 JSON 后附加 Excess 文本（如 "Observation:" 片段），
    导致 json.loads 报 "Extra data" 错误。

    策略:
      1. 查找第一个 { 和对应的 }，只解析那个 JSON 对象
      2. 如果不是 JSON，尝试 key=value 行解析
      3. 兜底返回 {"query": raw_string}
    """
    import json
    import re

    raw = tool_input.strip() if isinstance(tool_input, str) else str(tool_input)

    # 1) 尝试提取 JSON 对象
    if "{" in raw:
        # 找到第一个 { 和匹配的 }
        start = raw.index("{")
        depth = 0
        end = start
        for i in range(start, len(raw)):
            if raw[i] == "{":
                depth += 1
            elif raw[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        try:
            return json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError):
            pass

    # 2) 尝试 key:value 或 key=value 行解析
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    kwargs = {}
    for line in lines:
        line = line.strip().strip(",").strip('"').strip("'")
        # "key": "value" or "key": value or key=value
        for sep in (":", "="):
            if sep in line:
                parts = line.split(sep, 1)
                key = parts[0].strip().strip('"').strip("'")
                val = parts[1].strip().strip('"').strip("'")
                if key and val:
                    kwargs[key] = val
                break

    if kwargs:
        return kwargs

    # 3) 兜底
    return {"query": raw}
