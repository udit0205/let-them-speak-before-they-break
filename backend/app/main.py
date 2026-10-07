from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .ai import generate_reply
from .config import get_settings
from .database import get_session, init_db
from .models import Conversation, Message, User, utc_now
from .prompts import MODE_PERSONALITIES
from .safety import assess, safety_response
from .schemas import ChatIn, ChatOut, MessageOut, ModeOut, SessionCreateIn, SessionOut

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_provider": settings.ai_provider, "app": settings.app_name}


@app.get("/api/modes", response_model=list[ModeOut])
def modes():
    return [
        ModeOut(id=mode_id, **data)
        for mode_id, data in MODE_PERSONALITIES.items()
    ]


def ensure_user(user_id: UUID, db: Session) -> User:
    user = db.get(User, user_id)
    if not user:
        user = User(id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def message_to_out(message: Message) -> MessageOut:
    return MessageOut(
        id=message.id,
        role=message.role,
        content=message.content,
        safety_flag=message.safety_flag,
        created_at=message.created_at,
    )


def request_user_id(x_user_id: UUID | None = Header(default=None, alias="X-User-ID")) -> UUID:
    if x_user_id is None:
        raise HTTPException(401, "Missing X-User-ID header")
    return x_user_id


@app.post("/api/sessions", response_model=SessionOut)
def create_session(payload: SessionCreateIn, db: Session = Depends(get_session), current_user: UUID = Depends(request_user_id)):
    if payload.user_id != current_user:
        raise HTTPException(403, "User mismatch")
    if payload.mode not in MODE_PERSONALITIES:
        raise HTTPException(400, "Unknown emotional mode")
    ensure_user(payload.user_id, db)
    now = utc_now()
    conversation = Conversation(
        user_id=payload.user_id,
        mode=payload.mode,
        title=MODE_PERSONALITIES[payload.mode]["label"],
        created_at=now,
        updated_at=now,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    opening = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=MODE_PERSONALITIES[payload.mode]["opening"],
    )
    db.add(opening)
    db.commit()
    return conversation


@app.get("/api/sessions/{user_id}", response_model=list[SessionOut])
def list_sessions(user_id: UUID, db: Session = Depends(get_session), current_user: UUID = Depends(request_user_id)):
    if user_id != current_user:
        raise HTTPException(403, "User mismatch")
    statement = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
    return db.exec(statement).all()


@app.get("/api/sessions/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(conversation_id: UUID, db: Session = Depends(get_session), current_user: UUID = Depends(request_user_id)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(404, "Conversation not found")
    if conversation.user_id != current_user:
        raise HTTPException(403, "Not your conversation")
    statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    return [message_to_out(item) for item in db.exec(statement).all()]


@app.post("/api/sessions/{conversation_id}/messages", response_model=ChatOut)
def chat(conversation_id: UUID, payload: ChatIn, db: Session = Depends(get_session), current_user: UUID = Depends(request_user_id)):
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(404, "Conversation not found")
    if conversation.user_id != current_user:
        raise HTTPException(403, "Not your conversation")

    user_message = Message(conversation_id=conversation_id, role="user", content=payload.content)
    assessment = assess(payload.content)
    user_message.safety_flag = assessment.level != "none"
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    history_rows = db.exec(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.desc()).limit(20)
    ).all()
    history_rows = list(reversed(history_rows))
    model_messages = [{"role": item.role, "content": item.content} for item in history_rows]

    if assessment.immediate_danger:
        reply = safety_response(settings.emergency_number, settings.mental_health_helpline)
        source = "safety"
    else:
        # Elevated-risk content is still handled by the model, but the system prompt
        # tells it to stay supportive and encourage real-world support where appropriate.
        reply, source = generate_reply(conversation.mode, model_messages)

    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply,
        safety_flag=assessment.immediate_danger,
    )
    db.add(assistant_message)
    conversation.updated_at = utc_now()
    if conversation.title == MODE_PERSONALITIES[conversation.mode]["label"]:
        cleaned = " ".join(payload.content.split())
        conversation.title = cleaned[:58] + ("…" if len(cleaned) > 58 else "")
    db.add(conversation)
    db.commit()
    db.refresh(assistant_message)

    return ChatOut(
        user_message=message_to_out(user_message),
        assistant_message=message_to_out(assistant_message),
        safety={
            "level": assessment.level,
            "immediate_danger": assessment.immediate_danger,
            "matched": assessment.matched,
            "ai_source": source,
            "emergency_number": settings.emergency_number,
            "mental_health_helpline": settings.mental_health_helpline,
        },
    )
