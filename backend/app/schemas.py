from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ModeOut(BaseModel):
    id: str
    label: str
    subtitle: str
    color: str
    icon: str
    opening: str


class SessionCreateIn(BaseModel):
    user_id: UUID
    mode: str


class SessionOut(BaseModel):
    id: UUID
    mode: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    id: UUID
    role: str
    content: str
    safety_flag: bool
    created_at: datetime


class ChatIn(BaseModel):
    content: str = Field(min_length=1, max_length=6000)


class ChatOut(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
    safety: dict
