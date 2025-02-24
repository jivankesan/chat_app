# app/routers/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.chat_session import ChatSession
from ..models.chat_message import ChatMessage
from ..schemas.chat_schemas import ChatRequest
from ..config import SECRET_KEY
from .auth import get_current_user
import openai, os

router = APIRouter()

@router.post("/start_chat")
def start_chat(session_name: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    chat_session = ChatSession(user_id=current_user.id, session_name=session_name)
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    return {"session_id": chat_session.id, "session_name": chat_session.session_name}

@router.get("/sessions")
def get_user_chats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()
    return [
        {
            "session_id": s.id,
            "session_name": s.session_name,
            "created_at": s.created_at
        } for s in sessions
    ]

@router.get("/messages/{session_id}")
def get_chat_messages(session_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    chat_session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp).all()
    return [
        {
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp
        } for m in messages
    ]

@router.post("/send_message")
def send_message_to_chat(req: ChatRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if req.session_id is None:
        raise HTTPException(status_code=400, detail="session_id is required")

    chat_session = db.query(ChatSession).filter(
        ChatSession.id == req.session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Save user message
    user_msg = ChatMessage(session_id=chat_session.id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Call OpenAI or Azure
    openai.api_key = os.getenv("OPENAI_API_KEY", "")
    try:
        response = openai.ChatCompletion.create(
            model=req.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": req.message},
            ],
            max_tokens=100,
            temperature=0.7
        )
        assistant_content = response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

    # Save assistant response
    assistant_msg = ChatMessage(session_id=chat_session.id, role="assistant", content=assistant_content)
    db.add(assistant_msg)
    db.commit()
    return {"assistant_response": assistant_content}

@router.get("/stream_chat")
def stream_chat(session_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Example SSE streaming
    from fastapi.responses import StreamingResponse
    import time

    chat_session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    def event_stream():
        yield "event: message\ndata: Streaming SSE response begins...\n\n"
        time.sleep(1)
        yield "event: message\ndata: Hello from SSE chunk 1\n\n"
        time.sleep(1)
        yield "event: message\ndata: Hello from SSE chunk 2\n\n"
        time.sleep(1)
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")