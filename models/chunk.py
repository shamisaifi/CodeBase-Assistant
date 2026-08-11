# models/chunk.py
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(384), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("code_files.id"), nullable=False)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)