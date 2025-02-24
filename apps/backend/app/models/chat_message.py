# app/models/chat_message.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from datetime import datetime
from sqlalchemy.orm import relationship
from ..database import Base
from .chat_session import ChatSession

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", backref="messages")