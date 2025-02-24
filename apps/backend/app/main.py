"""
main.py - A single-file FastAPI backend for a ChatGPT-like application.

Features:
1) JWT-Based User Authentication
2) Model Switching
3) SSE for Chat Streaming
4) Chat Sessions & Message History
5) File Upload (document ingestion)
6) Ask Questions (can be extended to RAG)
"""

import os
import time
import datetime
from typing import Optional, List
from io import BytesIO

import uvicorn
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Body,
    status,
    Request
)
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
# If you want to store embeddings in Postgres with pgvector:
# from pgvector.sqlalchemy import Vector

import openai

# ------------------------------------------------------------------------------
# 1. FastAPI App Initialization
# ------------------------------------------------------------------------------
app = FastAPI(title="My ChatGPT-like Backend")

# ------------------------------------------------------------------------------
# 2. Database Setup (SQLAlchemy)
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db") 
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------------------------------------------------------
# 3. Models (SQLAlchemy)
# ------------------------------------------------------------------------------
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
    session_name = Column(String, default="Untitled")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="chat_sessions")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", backref="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    text_content = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="documents")
    # If storing embeddings in Postgres (pgvector):
    # embedding = Column(Vector(dim=1536))

Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------------------------
# 4. Auth Configuration (JWT)
# ------------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # Decode JWT
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user_id: int = payload.get("user_id")
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# ------------------------------------------------------------------------------
# 5. Pydantic Schemas
# ------------------------------------------------------------------------------
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    message: str
    model_name: str = "gpt-3.5-turbo"  # or "gpt-4", "azure-deployment", etc.

class FileUploadResponse(BaseModel):
    msg: str
    document_id: int

class AskQuestionRequest(BaseModel):
    question: str
    model_name: str = "gpt-3.5-turbo"

# ------------------------------------------------------------------------------
# 6. Authentication Endpoints
# ------------------------------------------------------------------------------
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user_obj = User(
        email=user.email,
        password_hash=get_password_hash(user.password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return {"msg": "User registered successfully", "user_id": user_obj.id}

@app.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------------------------------------------------------------------
# 7. Chat Endpoints
# ------------------------------------------------------------------------------
@app.post("/start_chat")
def start_chat(session_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new chat session."""
    chat_session = ChatSession(user_id=current_user.id, session_name=session_name)
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    return {"session_id": chat_session.id, "session_name": chat_session.session_name}

@app.get("/chats")
def get_user_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all chat sessions for the current user."""
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()
    return [
        {
            "session_id": s.id,
            "session_name": s.session_name,
            "created_at": s.created_at
        } for s in sessions
    ]

@app.get("/chat_messages/{session_id}")
def get_chat_messages(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch previous messages in a specific chat session."""
    chat_session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
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

@app.post("/chat")
def send_message_to_chat(req: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Send a single message and get a single response (non-streaming).
    For SSE streaming, see /stream_chat below.
    """
    # 1) Verify chat session
    if req.session_id is None:
        raise HTTPException(status_code=400, detail="session_id is required")

    chat_session = db.query(ChatSession).filter(
        ChatSession.id == req.session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # 2) Save user message
    user_msg = ChatMessage(
        session_id=chat_session.id,
        role="user",
        content=req.message
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 3) Call OpenAI / Azure OpenAI
    #    (Assuming you set OPENAI_API_KEY or use Azure with appropriate env vars)
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
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

    # 4) Save assistant response
    assistant_msg = ChatMessage(
        session_id=chat_session.id,
        role="assistant",
        content=assistant_content
    )
    db.add(assistant_msg)
    db.commit()

    return {"assistant_response": assistant_content}

@app.get("/stream_chat")
def stream_chat(session_id: int, model_name: str = "gpt-3.5-turbo", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    SSE endpoint to stream the AI assistant's response token-by-token.
    This is a simplified example. In production, handle concurrency carefully.
    """
    chat_session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    def event_stream():
        # Example logic to yield streaming data
        # In practice, you can use openai.ChatCompletion.create(stream=True)
        # and yield chunks as SSE
        yield "event: message\ndata: Streaming SSE response begins...\n\n"
        time.sleep(1)
        yield "event: message\ndata: Hello from SSE chunk 1\n\n"
        time.sleep(1)
        yield "event: message\ndata: Hello from SSE chunk 2\n\n"
        time.sleep(1)
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# ------------------------------------------------------------------------------
# 8. Document Upload & Question (RAG-like endpoint)
# ------------------------------------------------------------------------------
@app.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document. In production, parse PDFs / docx, generate embeddings, etc.
    """
    content = await file.read()
    text_content = content.decode("utf-8", errors="ignore")  # simplistic approach

    new_doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        text_content=text_content
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # TODO: generate embeddings, store them in doc or external vector DB
    return {"msg": "File uploaded", "document_id": new_doc.id}

@app.post("/ask_question")
def ask_question(req: AskQuestionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    A stub for a RAG-based approach:
    1) Embed the question
    2) Retrieve relevant doc chunks
    3) Construct prompt with context
    4) Call LLM
    """
    # (1) embed question => query vector store (omitted here)
    # (2) retrieve doc text => we skip actual retrieval in this example
    fake_context = "Context from retrieved documents would go here..."

    prompt = f"""
    You are a helpful AI. Use the following context to answer the question:
    Context: {fake_context}
    Question: {req.question}
    Answer:
    """

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        response = openai.ChatCompletion.create(
            model=req.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        answer = response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"answer": answer}

# ------------------------------------------------------------------------------
# 9. Run the App
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)