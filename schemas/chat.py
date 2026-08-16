from datetime import datetime

from pydantic import BaseModel, Field


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

class MessageResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    content: str
    sender: str
    session_id: int
    created_at: datetime

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    model_config = {"from_attributes": True}
    user_message: str
    ai_response: str
    session_id: int