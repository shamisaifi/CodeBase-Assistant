from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

from models.auth import User
from models.chat import ChatMessage, ChatSession
from models.chunk import CodeChunk
from models.file import CodeFile
