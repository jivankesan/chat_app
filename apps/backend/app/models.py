# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="sessions")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", backref="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    text_content = Column(Text)
    # You can store embeddings in a vector column if using pgvector:
    # embedding = Column(Vector(dimension=1536))  # dimension depends on model
    metadata = Column(JSONB)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="documents")