from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    session_name: str

class SessionResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    session_name: str
    user_id: int
    created_at: datetime

class FileResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    file_name: str
    file_size: int
    file_type: str
    is_processed: bool
    created_at: datetime

class UploadResponse(BaseModel):
    session: SessionResponse
    files: list[FileResponse]
    invalid_files: list[str]
