from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)


class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="user.id")
    mode: str = Field(index=True, max_length=32)
    title: str = Field(default="New conversation", max_length=120)
    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(index=True, foreign_key="conversation.id")
    role: str = Field(max_length=20)
    content: str
    safety_flag: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now, index=True)
