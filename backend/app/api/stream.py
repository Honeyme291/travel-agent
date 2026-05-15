"""
SSE 流式输出 API — GET /api/chat/stream
"""
import json
import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.agent.workflow import TravelAgentWorkflow
from app.memory.redis_session import get_session_manager, RedisSessionManager

router = APIRouter()


@router.get("/chat/stream")
async def chat_stream(request: Request, query: str, session_id: str = "default"):
    """
    SSE 流式聊天

    客户端使用:
        const es = new EventSource('/api/chat/stream?query=...&session_id=...');
        es.onmessage = (e) => { ... };
    """
    async def generate():
        # 初始化
        redis_sess = await get_session_manager()
        context = await redis_sess.get_context(session_id)

        yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"

        wf = TravelAgentWorkflow()
        state = await wf.run(query, session_id, context)

        plan = state.get("plan", {})

        if not plan.get("need_tools"):
            # 简单回复
            answer = state.get("final_answer", "")
            # Simulate streaming by yielding words
            words = answer.split()
            for i in range(0, len(words), 5):
                chunk = " ".join(words[i:i+5])
                yield f"data: {json.dumps({'type': 'text', 'content': chunk + ' '})}\n\n"
                await asyncio.sleep(0.05)
        else:
            tasks = plan.get("tasks", [])
            yield f"data: {json.dumps({'type': 'status', 'content': f'正在执行: {tasks}'})}\n\n"

            # 天气
            if state.get("weather"):
                yield f"data: {json.dumps({'type': 'weather', 'content': state['weather'][:300]})}\n\n"

            # 路线
            if state.get("route"):
                yield f"data: {json.dumps({'type': 'route', 'content': state['route']})}\n\n"

            # 最终回复
            answer = state.get("final_answer", "")
            words = answer.split()
            for i in range(0, len(words), 5):
                chunk = " ".join(words[i:i+5])
                yield f"data: {json.dumps({'type': 'text', 'content': chunk + ' '})}\n\n"
                await asyncio.sleep(0.05)

        # 保存到缓存
        await redis_sess.add_message(session_id, "user", query)
        await redis_sess.add_message(session_id, "assistant", state.get("final_answer", ""))

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
