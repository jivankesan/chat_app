# app/documents.py
from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Document
from .auth import get_db

documents_router = APIRouter()

@documents_router.post("/upload")
async def upload_document(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Read file content
    content = await file.read()

    # Optional: parse PDF, DOCX, etc. to extract text
    text_content = content.decode("utf-8", errors="ignore")

    # Insert into DB
    doc = Document(
        user_id=user_id,
        filename=file.filename,
        text_content=text_content
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Generate embeddings asynchronously or right here
    # store in doc.embedding (if using pgvector) or external vector DB
    return {"msg": "File uploaded", "document_id": doc.id}