from typing import Annotated

import redis.asyncio as redis
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user, get_db, get_redis
from models.auth import User
from models.chat import ChatMessage, ChatSession
from models.file import CodeFile
from services.file_handling_service import save_file_to_db, validate_files

router = APIRouter()

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
RedisClient = Annotated[redis.Redis, Depends(get_redis)]


@router.post("/upload-file")
async def upload_file(
    current_user: CurrentUser,
    db: DBSession,
    files: list[UploadFile] = File(...)
):
    result = validate_files(files)
    file_ids = await save_file_to_db(result['valid_files'], "uploads/codes", current_user, None)

    # will use these file ids for rag like chunking , embed, vectore and many more

    return {"message": 'uploaded'}
