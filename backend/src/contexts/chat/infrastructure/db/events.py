# infrastructure/db/events.py
from typing import Set
from sqlalchemy import event, select, update, func
from sqlalchemy.orm import Session, sessionmaker
from src.contexts.chat.infrastructure.db.orm import conversations, messages_excl_sysPrompt  # your Table objects
from src.contexts.chat.domain.models import Conversation

def register_last_message_at_events(SessionFactory: sessionmaker) -> None:
    @event.listens_for(SessionFactory, "before_flush")
    def _collect_conversation_ids(session: Session, flush_context, instances):
        ids: Set[str] = session.info.setdefault("last_msg_touch_ids", set())
        # any Conversation made dirty/new by message changes will appear here
        for obj in session.new.union(session.dirty).union(session.deleted):
            if isinstance(obj, Conversation) and obj.id is not None:
                ids.add(obj.id)

    @event.listens_for(SessionFactory, "after_flush_postexec")
    def _update_last_message_at(session: Session, flush_context):
        ids: Set[str] | None = session.info.pop("last_msg_touch_ids", None)
        if not ids:
            return
        stmt = (
            update(conversations)
            .where(conversations.c.id.in_(ids))
            .values(
                last_message_at=select(func.max(messages_excl_sysPrompt.c.created_at))
                .where(messages_excl_sysPrompt.c.conversation_id == conversations.c.id)
                .correlate(conversations)
                .scalar_subquery()
            )
        )
        session.execute(stmt)
        # Splitting in two sets/cases: Conversation with new messages (check only new message created ats instead of all) and conversations where we also deleted messages is not worth the efficiency gain 
