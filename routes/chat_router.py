from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user, get_db
from models.auth import User
from schemas.chat import FileResponse, SessionResponse, UploadResponse
from services.file_handling_service import save_file_to_db, validate_files
from services.rag_service import process_files_for_rag
from services.session_service import (
    create_session,
    get_session_by_id,
    get_user_sessions,
)

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
    background_tasks.add_task(process_files_for_rag, file_data, db)


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
