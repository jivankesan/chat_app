# app/main.py

import uvicorn
from fastapi import FastAPI

from .database import Base, engine
from .routers import auth, chat, upload, ask_question  # your route files

# Make sure models are imported, so SQLAlchemy can see them
from .models import user, chat_session, chat_message, document

def create_app() -> FastAPI:
    app = FastAPI(title="My ChatGPT-like Backend")

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Include routers
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(chat.router, prefix="/chat", tags=["chat"])
    app.include_router(upload.router, prefix="/upload", tags=["upload"])
    app.include_router(ask_question.router, prefix="/ask", tags=["ask"])

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)