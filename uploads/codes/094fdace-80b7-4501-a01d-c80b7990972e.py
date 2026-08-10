import os
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile

ALLOWED_FILE_CONTENT = ["image/jpg", "image/jpeg", "image/png", "image/png"]
ALLOWED_FILE_SIZE = 2 * 1024 * 1024

def validate_image_service(file: UploadFile):
    if file.content_type not in ALLOWED_FILE_CONTENT:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} not allowed. Use JPEG, PNG, or WebP"
        )

    if file.size > ALLOWED_FILE_SIZE:
         raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is 2MB. Uploaded image size is {file.size}"
        )


def generate_file_name(original_file_name: str) -> str:
    ext = os.path.splitext(original_file_name)[1].lower()
    return f"{uuid.uuid4()}{ext}"


async def save_to_disk(file: UploadFile, directory: str) -> str:
    os.makedirs(directory, exist_ok=True)

    filename = generate_file_name(file.filename)
    file_path = os.path.join(directory, filename)

    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(1024*1024):
            await f.write(chunk)

    return file_path


# for latter
async def save_to_cloudinaryk(file: UploadFile):
    pass 