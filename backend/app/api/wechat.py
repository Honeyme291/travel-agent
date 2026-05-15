"""
微信公众号回调 API — GET/POST /api/wechat/callback
"""
from fastapi import APIRouter, Request, Query, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.wechat.crypto import check_signature
from app.wechat.handler import parse_wechat_message, handle_wechat_message
from app.agent.workflow import run_travel_agent
from app.memory.redis_session import get_session_manager
from app.memory import RedisSessionManager
from app.models.database import get_db
from app.agent.memory_agent import memory_agent

router = APIRouter(prefix="/wechat")


@router.get("/callback")
async def wechat_verify(
    signature: str = Query(""),
    timestamp: str = Query(""),
    nonce: str = Query(""),
    echostr: str = Query(""),
):
    """微信服务器 GET 验证"""
    if check_signature(signature, timestamp, nonce):
        return Response(content=echostr, media_type="text/plain")
    return Response(content="signature failed", status_code=403)


@router.post("/callback")
async def wechat_callback(
    request: Request,
    signature: str = Query(""),
    timestamp: str = Query(""),
    nonce: str = Query(""),
    db: AsyncSession = Depends(get_db),
):
    """微信消息回调 — POST"""
    # 签名验证
    if not check_signature(signature, timestamp, nonce):
        return Response(content="signature failed", status_code=403)

    xml_body = await request.body()
    msg = parse_wechat_message(xml_body.decode())

    # 获取或创建 Session
    session_id = RedisSessionManager.openid_to_session(msg.from_user)

    # 生成回复
    reply = await handle_wechat_message(msg)

    if reply.content == "__AGENT_PROCESSING__":
        # 调用 Agent
        redis_sess = await get_session_manager()
        context = await redis_sess.get_context(session_id)
        agent_answer = await run_travel_agent(msg.content, session_id, context)

        # 持久化
        await memory_agent.save_message(db, session_id, "user", msg.content)
        await memory_agent.save_message(db, session_id, "assistant", agent_answer)
        await redis_sess.add_message(session_id, "user", msg.content)
        await redis_sess.add_message(session_id, "assistant", agent_answer)

        reply.content = agent_answer

    return Response(content=reply.to_xml(), media_type="application/xml")
