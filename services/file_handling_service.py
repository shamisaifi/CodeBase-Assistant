
import os
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from models.file import CodeFile

ALLOWED_CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".cpp", ".c",
    ".html", ".css", ".json", ".yaml", ".md",
}

MAX_CODE_FILE_SIZE = 10 * 1024 * 1024  # 10MB
CHUNK_SIZE = 1024 * 1024  # 1MB chunks


def validate_files(files: list[UploadFile]) -> dict:
    """
    Separates files into valid and invalid.
    Does NOT raise — caller decides what to do with invalid files.
    """
    valid_files = []
    invalid_files = []

    for file in files:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_CODE_EXTENSIONS:
            invalid_files.append(file)
            continue
        if file.size and file.size > MAX_CODE_FILE_SIZE:
            invalid_files.append(file)
            continue
        valid_files.append(file)

    return {"valid_files": valid_files, "invalid_files": invalid_files}


def _generate_unique_filename(original: str) -> str:
    ext = os.path.splitext(original)[1].lower()
    return f"{uuid.uuid4()}{ext}"


async def _write_file_to_disk(file: UploadFile, file_path: str) -> None:
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(CHUNK_SIZE):
            await f.write(chunk)


async def save_file_to_db(
    files: list[UploadFile],
    session_id: int,
    user_id: int,
    directory: str,
    db: AsyncSession,
) -> list[CodeFile]:
    
    os.makedirs(directory, exist_ok=True)

    new_files: list[CodeFile] = []
    saved_paths: list[str] = []

    try:
        for file in files:
            file_name = _generate_unique_filename(file.filename or "upload")
            file_path = os.path.join(directory, file_name)

            await _write_file_to_disk(file, file_path)
            saved_paths.append(file_path)

            new_file = CodeFile(
                file_name=file.filename,
                file_size=file.size or 0,
                file_path=file_path,
                file_type=os.path.splitext(file_name)[1],
                user_id=user_id,
                chat_session_id=session_id,
                is_processed=False,
            )
            db.add(new_file)
            new_files.append(new_file)

        await db.commit()

        for f in new_files:
            await db.refresh(f)

        return new_files

    except Exception as e:
        await db.rollback()
        for path in saved_paths:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    