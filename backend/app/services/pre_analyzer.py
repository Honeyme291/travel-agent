"""
预分析服务 — 判断场景类型，决定使用简单模式还是深度分析模式
"""
import json
from datetime import datetime
from typing import Any, Dict

from app.core.llm import get_llm
from app.schemas.models import Extraction, MultiDestInfo, PreAnalysisResult


# ── 多目的地检测 ──
ROUNDTRIP_KEYWORDS = ["往返", "来回", "回程", "返程", "返回"]
MULTI_DEST_KEYWORDS = [
    "再去", "然后去", "接着去", "顺便去",
    "再到", "然后到", "接着到",
    "再去看看", "再看看", "之后去", "之后到",
]


def detect_multi_destination(user_query: str, extraction: Extraction) -> MultiDestInfo:
    """检测是否为多目的地场景"""
    # 优先排除往返
    if any(kw in user_query for kw in ROUNDTRIP_KEYWORDS):
        return MultiDestInfo(
            is_multi_destination=False,
            raw_destination_text=extraction.destination,
            detection_method="roundtrip_excluded",
        )

    # 关键词检测
    detected = [kw for kw in MULTI_DEST_KEYWORDS if kw in user_query]
    if detected:
        return MultiDestInfo(
            is_multi_destination=True,
            detected_keywords=detected,
            raw_destination_text=extraction.destination,
            detection_method="keyword",
        )

    # 逗号分隔检测
    dest = extraction.destination or ""
    norm = dest.replace(",", "，").replace("、", "，").replace("和", "，")
    cities = [c.strip() for c in norm.split("，") if c.strip()]

    unique = list(dict.fromkeys(cities))

    if len(unique) >= 3:
        return MultiDestInfo(
            is_multi_destination=True,
            raw_destination_text=dest,
            detection_method="comma_separated_3plus",
        )
    if len(unique) == 2 and extraction.origin not in unique:
        return MultiDestInfo(
            is_multi_destination=True,
            raw_destination_text=dest,
            detection_method="comma_separated_2",
        )

    return MultiDestInfo(raw_destination_text=dest)


# ── LLM 预分析 ──
def pre_analyze_query(user_query: str) -> PreAnalysisResult:
    """使用 LLM 提取关键信息并判断场景类型"""
    llm = get_llm()
    today = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().year

    prompt = f"""You are a travel planning assistant. Today's date is {today}.

Your task: Extract key information from the user query and determine if it needs deep analysis.

RULES:
- Output ONLY valid JSON. NO explanations, NO markdown code blocks.
- Date conversion: "今天"/"today" = {today}, "明天"/"tomorrow" = +1 day, etc.
- Use Chinese for city names.
- Set "needs_deep_analysis" to true if:
  * Complex multi-city routes
  * Budget optimization needed
  * Multiple conflicting constraints
  * Special needs: 老人, 小孩, 儿童, etc.

Output this exact JSON structure:
{{
  "destination": "extracted destination city or cities",
  "origin": "extracted origin city",
  "travel_days": 0,
  "budget": 0,
  "travel_date": "YYYY-MM-DD",
  "preferences": [],
  "needs_deep_analysis": false,
  "has_special_needs": false
}}

User query: {user_query}"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            if content.startswith("json"):
                content = content[4:]

        extraction = Extraction(**json.loads(content))
    except Exception:
        extraction = Extraction()

    multi_dest_info = detect_multi_destination(user_query, extraction)

    if multi_dest_info.is_multi_destination:
        scenario_type = "multi_destination"
        needs_r1 = True
    elif extraction.needs_deep_analysis or extraction.has_special_needs:
        scenario_type = "complex"
        needs_r1 = True
    else:
        scenario_type = "simple"
        needs_r1 = False

    return PreAnalysisResult(
        scenario_type=scenario_type,
        needs_deep_analysis=needs_r1,
        extraction=extraction,
        multi_dest_info=multi_dest_info,
    )
