"""
聊天 API — POST /api/chat，自动附带景点图片 + 持久化到 PostgreSQL
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.models import ChatRequest, ChatResponse
from app.services.travel_service import travel_service
from app.agent.image_agent import get_spot_cards
from app.models.database import get_db
from app.agent.memory_agent import memory_agent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """处理旅行规划聊天请求，自动搜索目的地景点图片并持久化消息"""
    result = await travel_service.chat(
        user_query=req.query,
        session_id=req.session_id,
        uploaded_files=req.upload_files,
    )

    # 自动搜索目的地景点图片（每个目的地独立一个卡片）
    spot_cards = []
    destination = result.get("destination", "")
    if destination:
        try:
            spot_cards = get_spot_cards(destination)
            print(f"[Chat] Generated {len(spot_cards)} spot cards for: {destination}")
        except Exception as e:
            print(f"[Chat] Spot cards failed for '{destination}': {e}")

    # 持久化消息到 PostgreSQL
    try:
        await memory_agent.save_message(db, req.session_id, "user", req.query, user_id=req.user_id)
        await memory_agent.save_message(db, req.session_id, "assistant", result["answer"], user_id=req.user_id)
    except Exception:
        pass  # DB 不可用时静默跳过

    return ChatResponse(
        session_id=result["session_id"],
        answer=result["answer"],
        scenario_type=result.get("scenario_type"),
        tool_calls_count=result.get("tool_calls_count", 0),
        destination=destination,
        spot_cards=spot_cards,
    )


@router.get("/spot-images")
async def spot_images(query: str = ""):
    """单独查询景点图片 — GET /api/spot-images?query=西湖"""
    if not query:
        return {"cards": [], "images": [], "description": ""}
    cards = get_spot_cards(query)
    if cards:
        card = cards[0]
        return {"cards": cards, "images": card["images"], "description": card["description"], "name": card["name"]}
    return {"cards": [], "images": [], "description": ""}
