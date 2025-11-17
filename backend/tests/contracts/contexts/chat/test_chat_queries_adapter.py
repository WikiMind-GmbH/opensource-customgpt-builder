from datetime import datetime, timezone, timedelta

from src.contexts.shared.typing_aliases import Factory
import pytest
from sqlalchemy import insert

from src.contexts.chat.infrastructure.adapters.chat_queries_sqlalchemy import (
    ChatQueriesAdapter,
)
from src.contexts.chat.infrastructure.db.orm import (
    conversations,
    messages_excl_sysPrompt,
)
from src.contexts.chat.domain.models import Role, ContentType
from src.contexts.chat.application.ports.chat_queries import (
    ConversationOverviewDTO,
    NotFoundError,
    RoleDTO,
)
from sqlalchemy.orm import Session


def test_get_chat_summaries_ordered_by_last_message(
    session_factory: Factory[Session], adapter: ChatQueriesAdapter
):
    """Returns (id, title) ordered by last_message_at DESC, NULLS LAST."""
    session: Session = session_factory()

    now = datetime.now(timezone.utc)
    older = now - timedelta(hours=1)
    newer = now + timedelta(hours=1)

    # convs: A(newer), B(older), C(None)
    session.execute(
        insert(conversations),
        [
            {"id": "A", "title": "Alpha", "last_message_at": newer},
            {"id": "B", "title": "Beta", "last_message_at": older},
            {"id": "C", "title": "Gamma", "last_message_at": None},
        ],
    )
    session.commit()

    items = adapter.get_chat_summaries_ordered_by_last_message()

    # Expect: A, B, then C (NULLS LAST)
    assert [c.id for c in items] == ["A", "B", "C"]
    assert [c.title for c in items] == ["Alpha", "Beta", "Gamma"]


def test_empty_get_chat_summaries_returns_empty_list(adapter: ChatQueriesAdapter):
    summaries: list[ConversationOverviewDTO] = (
        adapter.get_chat_summaries_ordered_by_last_message()
    )
    assert summaries == []


def test_chat_history_returns_correct_cgpt_value(
    session_factory: Factory[Session], adapter: ChatQueriesAdapter
):
    session = session_factory()

    # Create conversation
    session.execute(
        insert(conversations).values(
            id="conv1", title="T", _customGPT_id="cgpt-123", last_message_at=None
        )
    )
    session.execute(
        insert(conversations).values(
            id="conv2", title="T", _customGPT_id=None, last_message_at=None
        )
    )
    session.commit()

    dto = adapter.get_chat_history("conv1")
    # customgpt id propagated
    assert dto.customgpt_id == "cgpt-123"

    dto2 = adapter.get_chat_history("conv2")
    # customgpt id propagated
    assert dto2.customgpt_id is None


def test_get_chat_history_returns_only_text_messages_and_maps_roles(
    session_factory: Factory[Session], adapter: ChatQueriesAdapter
):
    """Only text messages are returned; roles are mapped; newest-first per adapter; includes customgpt id."""
    session = session_factory()

    # Create conversation
    session.execute(
        insert(conversations).values(
            id="conv1", title="T", _customGPT_id="cgpt-123", last_message_at=None
        )
    )

    # Insert mixed messages for conv1 (text + image)
    session.execute(
        insert(messages_excl_sysPrompt),
        [
            {
                "conversation_id": "conv1",
                "role": Role.user,
                "contentType": ContentType.text,
                "imageUrlOrText": "hello",
                "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            },
            {
                "conversation_id": "conv1",
                "role": Role.assistant,
                "contentType": ContentType.image,
                "imageUrlOrText": "http://img/1.png",
                "created_at": datetime(2024, 1, 2, tzinfo=timezone.utc),
            },
            {
                "conversation_id": "conv1",
                "role": Role.assistant,
                "contentType": ContentType.text,
                "imageUrlOrText": "hi!",
                "created_at": datetime(2024, 1, 3, tzinfo=timezone.utc),
            },
        ],
    )
    session.commit()

    dto = adapter.get_chat_history("conv1")

    # customgpt id propagated
    assert dto.customgpt_id == "cgpt-123"

    # Only TEXT messages, sorted by created_at DESC per adapter
    assert [m.text for m in dto.messages] == [ "hello","hi!"]
    assert [m.role for m in dto.messages] == [RoleDTO.user,RoleDTO.assistant]


def test_get_chat_history_unknown_conversation_raises(adapter: ChatQueriesAdapter):
    non_existent_conv_id = "does-not-exist"

    with pytest.raises(NotFoundError) as exc:
        adapter.get_chat_history(non_existent_conv_id)

    assert f"No Conv with id {non_existent_conv_id} exists" in str(exc.value)


def test_sessions_are_closed(
    session_factory: Factory[Session], adapter: ChatQueriesAdapter
):
    """Returns (id, title) ordered by last_message_at DESC, NULLS LAST."""
    session: Session = session_factory()

    now = datetime.now(timezone.utc)

    # convs: A(newer), B(older), C(None)
    session.execute(
        insert(conversations),
        [
            {"id": "A", "title": "Alpha", "last_message_at": now},
        ],
    )
    session.commit()
    for n in range(10):
        items = adapter.get_chat_summaries_ordered_by_last_message()