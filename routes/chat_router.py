from typing import Annotated

from dependencies import get_current_user, get_db
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from models.auth import User
from models.chat import ChatMessage
from models.file import CodeFile
from schemas.chat import (
    ChatRequest,
    ChatResponse,
    FileResponse,
    MessageResponse,
    SessionResponse,
    UploadResponse,
)
from services.file_handling_service import save_file_to_db, validate_files
from services.rag_service import process_files_for_rag, rag_search
from services.session_service import (
    create_session,
    get_session_by_id,
    get_user_sessions,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/new-session", response_model=UploadResponse)
async def new_session(
    current_user: CurrentUser,
    db: DBSession,
    background_tasks: BackgroundTasks,
    session_name: str = Form(..., min_length=1, max_length=255),
    files: list[UploadFile] = File(...),
):
    validation = validate_files(files)

    if not validation["valid_files"]:
        raise HTTPException(
            status_code=400,
            detail=f"No valid files. Rejected: {[f.filename for f in validation['invalid_files']]}"
        )

    session = await create_session(session_name, current_user.id, db)
    saved_files = await save_file_to_db(
        validation["valid_files"], session.id, current_user.id, "uploads/codes", db
    )

    # RAG processing starts here as background task (implement when ready)
    file_data = [(f.id, f.file_path) for f in saved_files]
    background_tasks.add_task(process_files_for_rag, file_data)


    return UploadResponse(
        session=SessionResponse.model_validate(session),
        files=[FileResponse.model_validate(f) for f in saved_files],
        invalid_files=[f.filename for f in validation["invalid_files"]],
    )


@router.get("/sessions", response_model=list[SessionResponse])
async def get_sessions(current_user: CurrentUser, db: DBSession):
    return await get_user_sessions(current_user.id, db)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, current_user: CurrentUser, db: DBSession):
    return await get_session_by_id(session_id, current_user.id, db)


@router.post("/sessions/{session_id}/upload-files", response_model=list[FileResponse])
async def upload_files_to_session(
    session_id: int,
    current_user: CurrentUser,
    db: DBSession,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...)
):
    session = await get_session_by_id(session_id, current_user.id, db)
    
    validation = validate_files(files)
    saved_files = await save_file_to_db(
            validation["valid_files"], session.id, current_user.id, "uploads/codes", db
        )
    file_data = [(f.id, f.file_path) for f in saved_files]
    background_tasks.add_task(process_files_for_rag, file_data)

    return saved_files


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: int,
    current_user: CurrentUser,
    db: DBSession
):
    session = await get_session_by_id(session_id, current_user.id, db)
        
    result = await db.execute(select(ChatMessage).where(ChatMessage.session_id == session.id))
    messages = result.scalars().all()
    return messages


@router.post("/sessions/{session_id}/chat", response_model=ChatResponse)
async def chat(
    session_id: int,
    data: ChatRequest,
    current_user: CurrentUser,
    db: DBSession
):
    await get_session_by_id(session_id, current_user.id, db)
    result = await db.execute(select(CodeFile).where(CodeFile.chat_session_id == session_id, CodeFile.is_processed == True))
    processed_files = result.scalars().all()

    if not processed_files:
        return {"message": "Files not found"}

    answer = await rag_search(data.message, session_id, db)
    user_message = ChatMessage(
            content = data.message,
            sender = "user",
            session_id = session_id,
        )
    
    ai_message = ChatMessage(
            content = answer,
            sender = "ai",
            session_id = session_id,
        )

    db.add(user_message)               # correct
    db.add(ai_message)

    await db.commit()

    await db.refresh(user_message)
    await db.refresh(ai_message)

    return ChatResponse(
        user_message=data.message,
        ai_response=answer,
        session_id=session_id
    )


@router.get("/sessions/{session_id}/files", response_model=list[FileResponse])
async def get_session_files(session_id: int, current_user: CurrentUser, db: DBSession):
    await get_session_by_id(session_id, current_user.id, db)
    result = await db.execute(
        select(CodeFile).where(CodeFile.chat_session_id == session_id)
    )
    return result.scalars().all()