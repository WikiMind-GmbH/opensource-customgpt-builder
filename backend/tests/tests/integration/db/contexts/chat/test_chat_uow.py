import pytest
from sqlalchemy.orm import Session

from src.contexts.chat.application.ports.chat_repo import ConversationNotFoundError
from src.contexts.chat.domain.models import Conversation
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.shared.typing_aliases import Factory


def test_uow_commit_persists(session_factory: Factory[Session]):
    # UoW takes a callable that returns a Session; sessionmaker fits

    with SQLAlchemyConversationUOW(session_factory) as uow:
        # create and persist via repo
        conv: Conversation = uow.conversation_repo.create_conversation()
        conv_id = conv.id
        conv.add_user_text_message("text")
        uow.commit()

    # new session/UoW → data should be there
    with SQLAlchemyConversationUOW(session_factory) as uow2:
        got = uow2.conversation_repo.get(conv_id)
        assert got is not None
        assert len(got.messages_excl_sysPrompt) == 1


def test_uow_commit_needs_to_be_done_manually(session_factory: Factory[Session]):
    with SQLAlchemyConversationUOW(session_factory=session_factory) as uow:
        conv: Conversation = uow.conversation_repo.create_conversation()
        conv_id = conv.id
        conv.add_user_text_message("text")

    with SQLAlchemyConversationUOW(session_factory) as uow2:
        with pytest.raises(Exception):
            _ = uow2.conversation_repo.get(conv_id)


def test_uow_rollback_on_exception(session_factory: Factory[Session]):
    # create and then raise to trigger rollback
    conv_id: str | None = None
    with pytest.raises(RuntimeError):
        with SQLAlchemyConversationUOW(session_factory) as tx:
            conv = tx.conversation_repo.create_conversation()
            conv_id = conv.id
            conv.add_user_text_message("temporary")
            raise RuntimeError("Error before exiting the uow should lead to rollback")

    assert conv_id is not None

    # after rollback, the specific ID must not exist
    with SQLAlchemyConversationUOW(session_factory) as tx2:
        with pytest.raises(ConversationNotFoundError):
            tx2.conversation_repo.get(conv_id)


def test_uow_reinitializes_after_context_exit(session_factory: Factory[Session]):
    uow = SQLAlchemyConversationUOW(session_factory)
    with uow as uow:
        assert uow.conversation_repo is not None
    # after exit, internals should be cleared (no leaks)
    assert getattr(uow, "_session") is None
    assert getattr(uow, "_sqla_conv_repo") is None
