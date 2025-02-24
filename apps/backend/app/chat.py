# app/chat.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import ChatSession, ChatMessage, User
from .auth import get_db
import time

chat_router = APIRouter()

@chat_router.post("/start_chat")
def start_chat(session_name: str, user_id: int, db: Session = Depends(get_db)):
    chat_session = ChatSession(user_id=user_id, session_name=session_name)
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    return {"session_id": chat_session.id}

@chat_router.get("/stream_chat")
async def stream_chat(session_id: int, db: Session = Depends(get_db)):
    """
    SSE or WebSocket streaming of chat. This is an SSE example.
    """
    def event_stream():
        while True:
            # This is a mock. In reality, you'd listen for new messages 
            # or generate messages from the LLM.
            time.sleep(1)
            yield f"data: Hello from session {session_id}!\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@chat_router.post("/ask_rag")
def ask_rag(question: str, user_id: int, model_name: str, db: Session = Depends(get_db)):
    query_embedding = embed_text(question)
    # 1) Retrieve top docs via similarity search
    # 2) Concatenate them into a context
    context = retrieve_relevant_context(query_embedding, db)

    # 3) Build prompt
    prompt = f"""You are a helpful AI. Use the following context to answer:
    {context}
    Question: {question}
    Answer:"""

    # 4) Call the LLM
    completion = openai.ChatCompletion.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        stream=False  # or True if you want streaming
    )
    answer = completion["choices"][0]["message"]["content"]
    
    return {"answer": answer}