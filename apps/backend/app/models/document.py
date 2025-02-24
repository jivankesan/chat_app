# app/models/document.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from datetime import datetime
from sqlalchemy.orm import relationship
from ..database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    text_content = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="documents")