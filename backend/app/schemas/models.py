"""
Pydantic 请求/响应模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Chat ──
class ChatRequest(BaseModel):
    session_id: str = "default"
    query: str = Field(..., min_length=1, description="用户输入的旅行需求")
    user_id: int | None = None
    upload_files: list = []


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    scenario_type: Optional[str] = None
    tool_calls_count: int = 0
    destination: Optional[str] = None
    spot_cards: list = []
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ── Pre-analysis ──
class Extraction(BaseModel):
    destination: str = ""
    origin: str = ""
    travel_days: int = 0
    budget: float = 0.0
    travel_date: str = ""
    preferences: list = []
    needs_deep_analysis: bool = False
    has_special_needs: bool = False


class MultiDestInfo(BaseModel):
    is_multi_destination: bool = False
    detected_keywords: list = []
    raw_destination_text: str = ""
    detection_method: str = ""


class PreAnalysisResult(BaseModel):
    scenario_type: str = "simple"
    needs_deep_analysis: bool = False
    extraction: Extraction = Field(default_factory=Extraction)
    multi_dest_info: MultiDestInfo = Field(default_factory=MultiDestInfo)


# ── Session ──
class SessionClearRequest(BaseModel):
    session_id: str = "default"


class SessionClearResponse(BaseModel):
    session_id: str
    cleared: bool = True


# ── Tools ──
class ToolInfo(BaseModel):
    name: str
    description: str


class ToolsListResponse(BaseModel):
    tools: list[ToolInfo]
    count: int


# ── Health ──
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    mcp_servers: list
