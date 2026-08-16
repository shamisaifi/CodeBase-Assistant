from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from models.auth import User
from models.file import CodeFile


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="chat_sessions")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="chat_session")
    files: Mapped[list["CodeFile"]] = relationship("CodeFile", foreign_keys="CodeFile.chat_session_id")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(String(10), nullable=False)  # "user" or "ai"
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)

    chat_session: Mapped["ChatSession"] = relationship(back_populates="chat_messages")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())