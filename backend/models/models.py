from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel

class ConversationDB(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    title: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    # foreign_key must match the actual table name 'customgptsdb'
    customgpt_id: int | None = Field(foreign_key="customgptsdb.id", index=True)

    messages: List["MessageDB"] = Relationship(back_populates="conversation")


class CustomGptsDB(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    custom_gpt_description: str
    custom_gpt_instructions: str


class MessageDB(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    conversation_id: int = Field(foreign_key="conversationdb.id", index=True)
    role: str
    content: str | None = None
    function_name: str | None = None
    function_args: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    conversation: Optional[ConversationDB] = Relationship(back_populates="messages")
