# app/schemas/chat_schemas.py

from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    message: str
    model_name: str = "gpt-3.5-turbo"

class FileUploadResponse(BaseModel):
    msg: str
    document_id: int

class AskQuestionRequest(BaseModel):
    question: str
    model_name: str = "gpt-3.5-turbo"