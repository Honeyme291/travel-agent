"""
JWT 工具 — Token 生成与验证
"""
import os
from datetime import datetime, timedelta

import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


def create_token(user_id: int, openid: str = "") -> str:
    """生成 JWT Token"""
    payload = {
        "user_id": user_id,
        "openid": openid,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """验证 JWT Token, 成功返回 payload, 失败返回 None"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def get_user_from_token(token: str) -> dict | None:
    """从 Token 中提取用户信息"""
    payload = verify_token(token)
    if payload:
        return {"user_id": payload["user_id"], "openid": payload.get("openid", "")}
    return None
