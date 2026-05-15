"""
旅行路线模型 — 路线JSON + 地图图片
"""
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class TravelRoute(Base):
    __tablename__ = "travel_routes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[str] = mapped_column(String(128), nullable=True, index=True)
    route_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    map_image: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="routes")
