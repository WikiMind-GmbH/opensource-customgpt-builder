import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.contexts.chat.application.ports.chat_repo import ConversationNotFoundError
from src.contexts.chat.domain.models import ContentType, Conversation, Message, Role
from src.contexts.chat.infrastructure.db.conv_repo_implmementations import (
    SQAlchemyConversartionRepository,
)
from src.contexts.chat.infrastructure.db.orm import (
    messages_excl_sysPrompt as messages_table,
)
from src.contexts.shared.typing_aliases import Factory


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
        with pytest.raises(ConversationNotFoundError):
            repository.get("non-existent-id")


def test_add_text_messages_domain_functions_translate(
    session_factory: Factory[Session],
):
    assistant_text: str = "assistant_text"
    user_text: str = "user_text"
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation = repository.create_conversation()
        conv_id: str = conversation.id
        conversation.add_user_text_message(user_text)
        session.commit()
        conversation.add_assistant_text_message(assistant_text)
        session.commit()
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conv: Conversation = repository.get(conv_id=conv_id)
        messages: list[Message] = conv.messages_excl_sysPrompt
        assert len(messages) == 2
        assert messages[0].contentType == ContentType.text
        assert messages[1].contentType == ContentType.text
        assert messages[0].role == Role.user
        assert messages[1].role == Role.assistant
        assert messages[0].imageUrlOrText == user_text
        assert messages[1].imageUrlOrText == assistant_text


def test_delete_conversation_cascades_messages(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation = repository.create_conversation()
        conversation.title = "X"
        conversation.add_user_text_message("hi")
        session.commit()

        repository.delete(conversation)
        session.commit()

    with session_factory() as verification_session:
        remaining_messages_count = verification_session.execute(
            select(func.count()).select_from(messages_table)
        ).scalar_one()
        assert remaining_messages_count == 0


def test_delete_conversations_with_cgpt(session_factory: Factory[Session]):
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        cgpt_id = "id"
        cgpt_other_id = "other_id"
        convs_with_cgpt: list[Conversation] = []
        unrelated_convs: list[Conversation] = []
        convs_with_cgpt.append(repository.create_conversation(cgpt_id=cgpt_id))
        convs_with_cgpt.append(repository.create_conversation(cgpt_id=cgpt_id))
        convs_with_cgpt.append(repository.create_conversation(cgpt_id=cgpt_id))

        conv_without_cgpt = repository.create_conversation()
        conv_with_other_cgpt = repository.create_conversation(cgpt_id=cgpt_other_id)
        unrelated_convs.append(conv_without_cgpt)
        unrelated_convs.append(conv_with_other_cgpt)

        all_convs: list[Conversation] = convs_with_cgpt + unrelated_convs
        session.commit()

    # Test: all convs exist
    with session_factory() as session:
        assert None not in [
            SQAlchemyConversartionRepository(session).get(conv.id) for conv in all_convs
        ]

    # delete
    with session_factory() as session:
        SQAlchemyConversartionRepository(session).delete_conversations_with_cgpt(
            cgpt_id=cgpt_id
        )
        session.commit()
    # Test: unrelated converstions still exist
    with session_factory() as session:
        assert None not in [
            SQAlchemyConversartionRepository(session).get(conv.id)
            for conv in unrelated_convs
        ]

    # Test: convs with cgpt_id were deleted
    with session_factory() as session:
        for conv in convs_with_cgpt:
            with pytest.raises(ConversationNotFoundError):
                SQAlchemyConversartionRepository(session).get(conv.id)


def test_add_user_text_message_roundtrip(session_factory: Factory[Session]):
    user_text = "user_text"
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation = repository.create_conversation()
        conversation.add_user_text_message(user_text)

        session.commit()

    with session_factory() as verification_session:
        repository_verify = SQAlchemyConversartionRepository(verification_session)
        fetched: Conversation = repository_verify.get(conversation.id)
        assert fetched.messages_excl_sysPrompt[0].role == Role.user
        assert fetched.messages_excl_sysPrompt[0].contentType == ContentType.text
        assert fetched.messages_excl_sysPrompt[0].imageUrlOrText == user_text


def test_add_assistant_text_message_roundtrip(session_factory: Factory[Session]):
    assistant_text = "assistant_text"
    with session_factory() as session:
        repository = SQAlchemyConversartionRepository(session)
        conversation = repository.create_conversation()
        conversation.add_assistant_text_message(assistant_text)

        session.commit()

    with session_factory() as verification_session:
        repository_verify = SQAlchemyConversartionRepository(verification_session)
        fetched: Conversation = repository_verify.get(conversation.id)
        assert fetched.messages_excl_sysPrompt[0].role == Role.assistant
        assert fetched.messages_excl_sysPrompt[0].contentType == ContentType.text
        assert fetched.messages_excl_sysPrompt[0].imageUrlOrText == assistant_text


# -----------------------------------------------------------------------------------
# RECREATE TESTS WITH PUBLIC INTERFACE INSTEAD OF PRIVATE ATTRIBUTE ONCE DELETE ADDED
# -----------------------------------------------------------------------------------
#
# def _fetch_last_message_at(session: Session, conversation_id: str):
#     return session.execute(
#         select(conversations_table.c.last_message_at).where(
#             conversations_table.c.id == conversation_id
#         )
#     ).scalar_one()
#
# def test_last_message_at_recomputes_on_delete_of_latest_message(
#     session_factory: Factory[Session],
# ):
#     with session_factory() as session:
#         repository = SQAlchemyConversartionRepository(session)
#         conversation = repository.create_conversation()
#         conversation.title = "LMA"

#         msg: Message = conversation.add_user_text_message("1")
#         session.commit()
#         assert msg is not None
#         timestamp_after_first = _fetch_last_message_at(session, conversation.id)

#         conversation.add_user_text_message("2")
#         session.commit()
#         timestamp_after_second = _fetch_last_message_at(session, conversation.id)
#         assert (
#             timestamp_after_second and timestamp_after_second >= timestamp_after_first
#         )

#         # Remove the latest message → timestamp should step yback
#         conversation._messages_excl_sysPrompt = conversation.messages_excl_sysPrompt[
#             :-1
#         ]
#         session.commit()
#         timestamp_after_deletion = _fetch_last_message_at(session, conversation.id)
#         assert timestamp_after_deletion == timestamp_after_first
#
# def test_last_message_at_becomes_null_when_all_messages_deleted(
#     session_factory: Factory[Session],
# ):
#     with session_factory() as session:
#         repository = SQAlchemyConversartionRepository(session)
#         conversation = repository.create_conversation()
#         conversation.add_user_text_message("x")
#         session.commit()
#         assert _fetch_last_message_at(session, conversation.id) is not None

#         conversation._messages_excl_sysPrompt.clear()  # delete-orphan
#         session.commit()
#         assert _fetch_last_message_at(session, conversation.id) is None
