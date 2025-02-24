# app/embeddings.py
import openai
from sqlalchemy.orm import Session
from .models import Document
# from pgvector.sqlalchemy import Vector  # If using pgvector

def embed_text(text: str) -> list[float]:
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]

def store_embedding_in_db(doc: Document, db: Session):
    embedding = embed_text(doc.text_content)
    # doc.embedding = embedding  # if using a Vector column
    # db.commit()
    # Or store in external vector DB (Pinecone, Weaviate, etc.)