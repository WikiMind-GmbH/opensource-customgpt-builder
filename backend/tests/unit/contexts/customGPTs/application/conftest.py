import pytest
from sqlalchemy import Connection, Engine, NullPool, RootTransaction, create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.infrastructure.adapters.conv_adapter import ConversationAdapter
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.infrastructure.db.orm import metadata as cgpt_metadata
from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.shared.typing_aliases import Factory

# --------------  CustomGPT UOW  -----------------


@pytest.fixture()
def cgpt_engine(start_cgpt_mappers):
    eng = create_engine(
        require_env("DB_URL_CGPT_TEST"), poolclass=NullPool
    )  # No connection pooling
    cgpt_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def cgpt_session_factory(cgpt_engine):
    """
    Provides a sessionmaker that creates NEW sessions, all bound to the same
    connection+outer transaction for this test.
    """
    connection: Connection = cgpt_engine.connect()
    outer_tx: RootTransaction = connection.begin()

    SessionFactory = sessionmaker(bind=connection, expire_on_commit=False)

    try:
        yield SessionFactory
    finally:
        outer_tx.rollback()
        connection.close()


@pytest.fixture()
def cgpt_uow_factory(cgpt_session_factory: Factory[Session]) -> Factory[CgptUOW]:
    return lambda: SQLAlchemyCgptUOW(session_factory=cgpt_session_factory)


# --------------  ConversationUOW  -----------------


@pytest.fixture()
def conv_engine(start_chat_mappers) -> Engine:
    eng = create_engine(
        require_env("DB_URL_CHAT_TEST"), poolclass=NullPool
    )  # No connection pooling
    chat_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def conv_session_factory(conv_engine):
    """
    Provides a sessionmaker that creates NEW sessions, all bound to the same
    connection+outer transaction for this test.
    """
    connection: Connection = conv_engine.connect()
    outer_tx: RootTransaction = connection.begin()

    SessionFactory = sessionmaker(bind=connection, expire_on_commit=False)
    register_last_message_at_events(SessionFactory)

    try:
        yield SessionFactory
    finally:
        outer_tx.rollback()
        connection.close()


@pytest.fixture()
def conv_uow_factory(conv_session_factory):
    return lambda: SQLAlchemyConversationUOW(session_factory=conv_session_factory)


@pytest.fixture()
def conversation_adapter_factory(
    conv_uow_factory: Factory[ConversationUOW],
) -> Factory[ConversationPort]:
    return lambda: ConversationAdapter(conv_uow_factory=conv_uow_factory)
