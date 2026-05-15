"""
认证 API — 注册 + JWT 登录
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.utils.jwt_utils import create_token, verify_token
from app.models.database import get_db
from app.models.user import User

router = APIRouter(prefix="/auth")


class RegisterRequest(BaseModel):
    username: str = ""
    password: str = ""
    nickname: str = ""
    openid: str = ""


class LoginRequest(BaseModel):
    username: str
    password: str


# ── 注册 ──
@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册 — 创建新用户并返回 JWT Token
    用于 Web 端：支持 username + password 注册
    用于微信端：直接传 openid 注册
    """
    username = req.username or req.openid or f"user_{req.nickname}"

    # 检查是否已存在
    result = await db.execute(select(User).where(User.openid == username))
    if result.scalar_one_or_none():
        # 已有用户，直接返回 Token
        existing = result.scalar_one()
        token = create_token(existing.id, existing.openid or username)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": existing.id,
            "nickname": existing.nickname or username,
            "is_new": False,
        }

    user = User(
        openid=username,
        nickname=req.nickname or username,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(user.id, user.openid or username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname or username,
        "is_new": True,
    }


# ── 登录 ──
@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录 — 验证用户名并返回 JWT Token"""
    result = await db.execute(select(User).where(User.openid == req.username))
    user = result.scalar_one_or_none()

    if not user:
        # 自动注册：首次登录直接创建用户
        user = User(openid=req.username, nickname=req.username)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_token(user.id, user.openid or req.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname or req.username,
    }


# ── Token 验证 ──
@router.get("/me")
async def me(token: str = ""):
    """验证 Token 并返回用户信息"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")
    return {
        "user_id": payload["user_id"],
        "openid": payload.get("openid", ""),
    }
