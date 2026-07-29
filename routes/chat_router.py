from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user, get_db
from models.auth import User
from schemas.chat import SessionResponse, UploadResponse
from services.file_handling_service import save_file_to_db, validate_files
from services.session_service import (
    create_session,
    get_session_by_id,
    get_user_sessions,
)

router = APIRouter()

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/new-session")
async def new_session(
    current_user: CurrentUser,
    db: DBSession,
    background_tasks: BackgroundTasks,
    session_name: str = Form(...),
    files: list[UploadFile] = File(...)
):
    # 1. validate files
    # 2. create session
    # 3. save valid files to disk and db
    # 4. background_tasks.add_task(process_files_for_rag, file_ids)  ← STOP POINT
    # 5. return UploadResponse
    user_id = current_user.id
    result = validate_files(files)
    session = await create_session(session_name, user_id,  db)
    await save_file_to_db(result["valid_files"], session.id, user_id, 'uploads/codes', db)
    return {"message": "session created and files are saved"}

@router.get("/sessions", response_model=list[SessionResponse])
async def get_sessions(
    current_user: CurrentUser, 
    db: DBSession
    ):
    result =  await get_user_sessions(current_user.id, db)
    return result
    

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, current_user: CurrentUser, db: DBSession):

    session = await get_session_by_id(session_id, current_user.id, db)

    return session