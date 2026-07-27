import os
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile

from models.file import CodeFile

ALLOWED_CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".cpp", ".c",
    ".html", ".css", ".json", ".yaml", ".md"
}

MAX_CODE_FILE_SIZE = 10 * 1024 * 1024


def validate_files(files: UploadFile):
    invalid_files = []
    valid_files = []

    print("files: ", files)
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in ALLOWED_CODE_EXTENSIONS or file.size > MAX_CODE_FILE_SIZE:
            invalid_files.append(file)
            continue

        valid_files.append(file)

    return {"invalid_files": invalid_files, "valid_files": valid_files}

def generate_file_name(file_name: str):
    ext = os.path.splitext(file_name)[1].lower()
    return f"{uuid.uuid4()}{ext}"


async def save_file_to_db(files: UploadFile, directory: str, current_user, db, session_id):
    file_ids = []

    for file in files:
        os.makedirs(directory, exist_ok=True)

        file_name = generate_file_name(file.filename)
        file_path = os.path.join(directory, file_name)

        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(1024*1024):
                await f.write(chunk)

        new_file = CodeFile(
            file_name=file_name,
            file_size=file.size,
            file_path=file_path,
            file_type=os.path.splitext(file_name)[1],
            user_id=current_user.id,
            chat_session_id=session_id
        )

        db.add(new_file)
        await db.commit()
        await db.refresh(new_file)

        file_ids.append(new_file.id)

    return file_ids
        