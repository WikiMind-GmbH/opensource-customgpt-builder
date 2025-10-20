from src.contexts.shared.typing_aliases import Factory
from src.contexts.chat.infrastructure.db.conv_repo_implmementations import (
    SQAlchemyConversartionRepository,
)
from src.contexts.chat.application.exceptions import ConversationNonExistentError
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.chat.domain.models import ContentType, Message, Role, Conversation
from src.contexts.chat.infrastructure.db.orm import conversations as conversations_table
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from sqlalchemy import select, func
from src.contexts.chat.infrastructure.db.orm import messages_excl_sysPrompt as messages_table
import itertools
import pytest


def test_repository_get_roundtrip(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        created_conversation = repository.create_conversation()
        created_conversation_id = created_conversation.id
        session.commit()

    with session_factory() as verification_session:
        verification_repository = SQAlchemyConversartionRepository(verification_session)
        fetched_conversation = verification_repository.get(created_conversation_id)
        assert fetched_conversation.id == created_conversation_id


def test_repository_get_raises_when_missing(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        with pytest.raises(ConversationNonExistentError):
            repository.get("non-existent-id")


def test_list_all_overviews_orders_by_last_message(session_factory: Factory[Session]):
    with session_factory() as session:
        conversation_a = Conversation(id="a")
        conversation_b = Conversation(id="b")
        conversation_c = Conversation(id="c")
        session.add_all([conversation_a, conversation_b, conversation_c])
        session.commit()

        conversation_a.messages_excl_sysPrompt.append(
            Message(role=Role.user, contentType=ContentType.text, imageUrlOrText="1")
        )
        session.commit()  # sets last_message_at for A

        conversation_b.messages_excl_sysPrompt.append(
            Message(role=Role.user, contentType=ContentType.text, imageUrlOrText="2")
        )
        session.commit()  # sets last_message_at for B (later than A)

        repository = SQAlchemyConversartionRepository(session)
        overviews = repository.list_all_overviews_ordered_by_latest_msg()
        assert [overview.id for overview in overviews] == ["b", "a", "c"]


def test_delete_conversation_cascades_messages(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation = repository.create_conversation()
        conversation.title = "X"
        conversation.messages_excl_sysPrompt.append(
            Message(role=Role.user, contentType=ContentType.text, imageUrlOrText="hi")
        )
        session.commit()

        repository.delete(conversation)
        session.commit()

    with session_factory() as verification_session:
        remaining_messages_count = verification_session.execute(
            select(func.count()).select_from(messages_table)
        ).scalar_one()
        assert remaining_messages_count == 0


def _fetch_last_message_at(session: Session, conversation_id: str):
    return session.execute(
        select(conversations_table.c.last_message_at).where(
            conversations_table.c.id == conversation_id
        )
    ).scalar_one()


def test_last_message_at_recomputes_on_delete_of_latest_message(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation = repository.create_conversation()
        conversation.title = "LMA"

        first_message = Message(
            role=Role.user, contentType=ContentType.text, imageUrlOrText="1"
        )
        conversation.messages_excl_sysPrompt.append(first_message)
        session.commit()
        timestamp_after_first = _fetch_last_message_at(session, conversation.id)

        second_message = Message(
            role=Role.user, contentType=ContentType.text, imageUrlOrText="2"
        )
        conversation.messages_excl_sysPrompt.append(second_message)
        session.commit()
        timestamp_after_second = _fetch_last_message_at(session, conversation.id)
        assert (
            timestamp_after_second and timestamp_after_second >= timestamp_after_first
        )

        # Remove the latest message → timestamp should step back
        conversation.messages_excl_sysPrompt.remove(second_message)
        session.commit()
        timestamp_after_deletion = _fetch_last_message_at(session, conversation.id)
        assert timestamp_after_deletion == timestamp_after_first


def test_last_message_at_becomes_null_when_all_messages_deleted(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation = repository.create_conversation()
        conversation.messages_excl_sysPrompt.append(
            Message(role=Role.user, contentType=ContentType.text, imageUrlOrText="x")
        )
        session.commit()
        assert _fetch_last_message_at(session, conversation.id) is not None

        conversation.messages_excl_sysPrompt.clear()  # delete-orphan
        session.commit()
        assert _fetch_last_message_at(session, conversation.id) is None


def test_overviews_empty_when_no_conversations(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        assert repository.list_all_overviews_ordered_by_latest_msg() == []


def test_overviews_place_null_last_message_at_last(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation_with_message = repository.create_conversation()
        conversation_with_message.title = "With"
        conversation_without_message = repository.create_conversation()
        conversation_without_message.title = "Without"

        conversation_with_message.messages_excl_sysPrompt.append(
            Message(role=Role.user, contentType=ContentType.text, imageUrlOrText="1")
        )
        session.commit()

        overview_ids = [
            overview.id
            for overview in repository.list_all_overviews_ordered_by_latest_msg()
        ]
        assert overview_ids == [
            conversation_with_message.id,
            conversation_without_message.id,
        ]


@pytest.mark.parametrize(
    "role,content_type", list(itertools.product(list(Role), list(ContentType)))
)
def test_message_enum_roundtrip(session_factory: Factory[Session], role: Role, content_type: ContentType):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation = repository.create_conversation()
        conversation.messages_excl_sysPrompt.append(
            Message(role=role, contentType=content_type, imageUrlOrText="x")
        )
        session.commit()

    with session_factory() as verification_session:
        repository_verify = SQAlchemyConversartionRepository(verification_session)
        fetched = repository_verify.get(conversation.id)
        assert fetched.messages_excl_sysPrompt[0].role == role
        assert fetched.messages_excl_sysPrompt[0].contentType == content_type
