import pytest
from src.contexts.chat.infrastructure.db.uow_implementations import SQLAlchemyConversationUOW
from src.contexts.chat.domain.models import Conversation, Message, Role, ContentType
from src.contexts.chat.application.exceptions import ConversationNonExistentError

def test_uow_commit_persists(session_factory):
    # UoW takes a callable that returns a Session; sessionmaker fits

    with SQLAlchemyConversationUOW(session_factory) as uow:
        # create and persist via repo
        conv: Conversation = uow.conversation_repo.create_conversation()
        conv_id = conv.id
        conv.messages_excl_sysPrompt.append(
            Message(role=Role.user, contentType=ContentType.text, imageUrlOrText="hello")
        )
        uow.commit()

    # new session/UoW → data should be there
    with SQLAlchemyConversationUOW(session_factory) as uow2:
        got = uow2.conversation_repo.get(conv_id)
        assert got is not None
        assert len(got.messages_excl_sysPrompt) == 1


def test_uow_rollback_on_exception(session_factory):
    # create and then raise to trigger rollback
    with pytest.raises(RuntimeError):
        with SQLAlchemyConversationUOW(session_factory) as tx:
            conv = tx.conversation_repo.create_conversation()
            conv_id = conv.id
            conv.messages_excl_sysPrompt.append(
                Message(role=Role.user, contentType=ContentType.text, imageUrlOrText="boom")
            )
            raise RuntimeError("Error before exiting the uow")

    # after rollback, the specific ID must not exist
    with SQLAlchemyConversationUOW(session_factory) as tx2:
        with pytest.raises(ConversationNonExistentError):
            tx2.conversation_repo.get(conv_id)


def test_uow_reinitializes_after_context_exit(session_factory):
    uow = SQLAlchemyConversationUOW(session_factory)
    with uow as uow:
        assert uow.conversation_repo is not None
    # after exit, internals should be cleared (no leaks)
    assert getattr(uow, "_session") is None
    assert getattr(uow, "_sqla_conv_repo") is None
