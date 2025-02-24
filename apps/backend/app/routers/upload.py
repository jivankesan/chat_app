# app/routers/upload.py

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.chat_schemas import FileUploadResponse
from .auth import get_current_user
from ..models.document import Document
from ..services.file_service import FileService
from ..services.embeddings_manager import EmbeddingsManager
from ..services.openai_client import OpenAIClient
from ..config import (MODEL_API_KEY, API_VERSION, MODEL_GENERATE, MODEL_EMBED, MODEL_ENDPOINT)

router = APIRouter()

@router.post("/", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    content = await file.read()

    # Use your FileService to process & embed
    # Usually you'd keep a single instance around, but for example:
    openai_client = OpenAIClient(config=type("Config", (), dict(
        MODEL_API_KEY=MODEL_API_KEY,
        API_VERSION=API_VERSION,
        MODEL_GENERATE=MODEL_GENERATE,
        MODEL_EMBED=MODEL_EMBED,
        MODEL_ENDPOINT=MODEL_ENDPOINT
    )))

    embeddings_manager = EmbeddingsManager()
    file_service = FileService(openai_client, None, embeddings_manager)

    file_service.process_file_for_user(str(current_user.id), content, file.filename)

    # Then store in DB if needed
    new_doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        text_content="(raw text or omitted for large docs...)"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return {"msg": "File uploaded", "document_id": new_doc.id}