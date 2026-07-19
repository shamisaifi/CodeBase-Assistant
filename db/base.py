from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from models.auth import User
from models.file import File
from models.chat import ChatSession