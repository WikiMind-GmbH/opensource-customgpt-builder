# adapters/orm.py
from datetime import datetime, timezone
from sqlalchemy import (
    Enum, Table, Column, String, Integer, DateTime, ForeignKey, MetaData
)
from sqlalchemy.orm import registry, relationship
from domain.models import ContentType, Conversation, Message, Role

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

conversations = Table(
    "conversations", metadata,
    Column("id", String, primary_key=True),
    Column("title", String, nullable= True),
    Column("customGPT_id", String, nullable=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False),
    Column("last_message_at", DateTime(timezone=True)),
)

messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("conversation_id", String, ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False),
    Column("role", Enum(Role, name = "role_enum"), nullable=False),
    Column("contentType", Enum(ContentType, name = "contenttype_enum"), nullable=False),
    Column("imageUrlOrText", String, nullable=False),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False),
)

def start_mappers() -> None:
    mapper_registry.map_imperatively(
        Message,
        messages,
    )
    mapper_registry.map_imperatively(
        Conversation,
        conversations,
        properties={
            # one-to-many; SQLAlchemy instruments `Conversation.messages`
            "messages": relationship(
                Message,
                primaryjoin=messages.c.conversation_id == conversations.c.id,
                backref=None,
                order_by=messages.c.id.asc(),
                cascade="all, delete-orphan",
                passive_deletes=True,
            )
        },
    )
