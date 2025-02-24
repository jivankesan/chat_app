# app/models/chat_session.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from ..database import Base
from .user import User

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_name = Column(String, default="Untitled")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="chat_sessions")