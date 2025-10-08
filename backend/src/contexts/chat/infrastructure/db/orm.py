# adapters/orm.py
from datetime import datetime, timezone
from sqlalchemy import (
    Engine,
    Enum,
    event,
    Index,
    Table,
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    MetaData,
)
from sqlalchemy.orm import registry, relationship
from src.contexts.chat.domain.models import ContentType, Conversation, Message, Role

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

conversations = Table(
    "conversations",
    metadata,
    Column("id", String, primary_key=True),
    Column("title", String, nullable=True),
    Column("customGPT_id", String, nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    ),
    Column("last_message_at", DateTime(timezone=True)),
)

messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "conversation_id",
        String,
        ForeignKey("conversations.id", ondelete="CASCADE"), # if the conversation with this id is deleted, this message row will be deleted as well -additionally need `PRAGMA foreign_keys=ON`
        index=True,
        nullable=False,
    ),
    Column("role", Enum(Role, name="role_enum",native_enum=False, validate_strings=True), nullable=False),
    Column("contentType", Enum(ContentType, name="contenttype_enum",native_enum=False, validate_strings=True), nullable=False),
    Column("imageUrlOrText", String, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    ),
)
def prepare_engine(engine: Engine) -> Engine:
    if engine.url.get_backend_name() == "sqlite":
        @event.listens_for(engine, "connect")
        def _fk_on(dbapi_conn, _):
            dbapi_conn.execute("PRAGMA foreign_keys=ON")
    return engine

# Index("ix_messages_conv_created_at", messages.c.conversation_id, messages.c.created_at)
## Later: alembic revision -m "add composite index" → write op.create_index('ix_messages_conv_created_at', 'messages', ['conversation_id', 'created_at']) → alembic upgrade head.
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
