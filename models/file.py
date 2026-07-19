from datetime import datetime
from db.base import Base
from sqlalchemy import String, Boolean, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    chat_session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())