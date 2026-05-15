"""
Image Agent — Wikimedia Commons 图片搜索 (MCP SSE) + AI 描述生成
"""
import os
import json

from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

from langchain_core.messages import HumanMessage
from app.core.llm import get_llm
from app.tools.base import run_async


WIKIMEDIA_MCP_URL = "https://mcp.api-inference.modelscope.net/04b887c4ed1941/sse"
WIKIMEDIA_API_KEY = os.getenv("WIKIMEDIA_APIKEY", "")


# ═══════════════════════════════════════
#  Placeholder 兜底
# ═══════════════════════════════════════

def _placeholder_images(query: str, count: int) -> list[dict]:
    """Wikimedia API Key 未配置时使用占位图"""
    from urllib.parse import quote
    encoded = quote(query)
    colors = ["2563eb", "7c3aed", "059669", "d97706", "dc2626"]
    return [{
        "url": f"https://placehold.co/600x400/{colors[i % 5]}/white?text={encoded}",
        "url_medium": f"https://placehold.co/300x200/{colors[i % 5]}/white?text={encoded}",
        "url_small": f"https://placehold.co/150x100/{colors[i % 5]}/white?text={encoded}",
        "url_original": "",
        "photographer": "",
        "photographer_url": "",
        "alt": query,
        "width": 600,
        "height": 400,
        "source": "placeholder",
        "license": "",
    } for i in range(count)]


# ═══════════════════════════════════════
#  Wikimedia MCP SSE 搜索
# ═══════════════════════════════════════

async def _search_wikimedia_raw(query: str, limit: int = 5) -> list[dict]:
    """通过 Wikimedia MCP SSE 搜索图片"""
    if not WIKIMEDIA_API_KEY:
        return []

    headers = {"XBY-APIKEY": WIKIMEDIA_API_KEY}
    try:
        async with sse_client(WIKIMEDIA_MCP_URL, headers=headers, timeout=15) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "wikimedia_search_images",
                    arguments={
                        "query": query,
                        "limit": limit,
                        "include_thumbnails": True,
                    },
                )
                if hasattr(result, "content") and result.content:
                    for c in result.content:
                        if hasattr(c, "text"):
                            try:
                                data = json.loads(c.text)
                                if isinstance(data, list):
                                    return data
                                if isinstance(data, dict) and "results" in data:
                                    return data["results"]
                            except json.JSONDecodeError:
                                pass
        return []
    except Exception as e:
        print(f"[Wikimedia] Search failed: {e}")
        return []


def _wikimedia_to_uniform(raw_item: dict) -> dict:
    """Wikimedia 原始结果 -> 统一图片格式"""
    return {
        "url": raw_item.get("url") or raw_item.get("image_url", ""),
        "url_medium": raw_item.get("thumb_url") or raw_item.get("thumbnail", ""),
        "url_small": raw_item.get("thumb_url") or raw_item.get("thumbnail", ""),
        "url_original": raw_item.get("url") or raw_item.get("image_url", ""),
        "photographer": raw_item.get("author") or raw_item.get("artist", "Wikimedia"),
        "photographer_url": raw_item.get("page_url") or raw_item.get("description_url", ""),
        "alt": raw_item.get("title") or raw_item.get("description", ""),
        "width": raw_item.get("width", 0),
        "height": raw_item.get("height", 0),
        "source": "wikimedia",
        "license": raw_item.get("license", ""),
    }


# ═══════════════════════════════════════
#  统一接口
# ═══════════════════════════════════════

def search_spot_images(spot_name: str, count: int = 4) -> list[dict]:
    """
    搜索景点图片 — Wikimedia MCP 优先，无 Key 则用占位图
    """
    if WIKIMEDIA_API_KEY:
        raw_results = run_async(_search_wikimedia_raw(spot_name, count))
        if raw_results:
            return [_wikimedia_to_uniform(r) for r in raw_results[:count]]

    return _placeholder_images(spot_name, count)


def generate_spot_description(spot_name: str) -> str:
    """LLM 生成景点介绍"""
    try:
        llm = get_llm()
        prompt = f"""请为以下景点写一段简短的介绍(80字以内):

景点: {spot_name}

要求: 生动、吸引人、包含关键特色"""
        resp = llm.invoke([HumanMessage(content=prompt)])
        return resp.content.strip()
    except Exception:
        return f"{spot_name}是一个值得一游的景点。"


def get_spot_card(spot_name: str) -> dict:
    """获取单个景点卡片: 图片列表 + AI 描述"""
    images = search_spot_images(spot_name, count=4)
    description = generate_spot_description(spot_name)
    return {"name": spot_name, "images": images, "description": description}


def get_spot_cards(destination_str: str) -> list[dict]:
    """解析目的地字符串（逗号/顿号分隔），为每个目的地生成卡片"""
    if not destination_str:
        return []

    norm = destination_str.replace("，", ",").replace("、", ",").replace("和", ",")
    cities = [c.strip() for c in norm.split(",") if c.strip()]

    seen = set()
    unique = []
    for c in cities:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    cards = []
    for city in unique[:5]:
        try:
            card = get_spot_card(city)
            cards.append(card)
        except Exception as e:
            print(f"[ImageAgent] Failed for '{city}': {e}")

    return cards
