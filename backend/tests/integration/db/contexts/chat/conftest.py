from collections.abc import Generator

import pytest
from sqlalchemy import Connection, Engine, NullPool, RootTransaction, create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata


@pytest.fixture(scope="session")
def engine(start_chat_mappers: None) -> Generator[Engine, None, None]:
    eng = create_engine(
        require_env("DB_URL_CHAT_TEST"), poolclass=NullPool
    )  # No connection pooling
    chat_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine: Engine) -> Generator[sessionmaker[Session], None, None]:
    """
    Provides a sessionmaker that creates NEW sessions, all bound to the same
    connection+outer transaction for this test.
    """
    connection: Connection = engine.connect()
    outer_tx: RootTransaction = connection.begin()

    SessionFactory = sessionmaker(bind=connection, expire_on_commit=False)
    register_last_message_at_events(SessionFactory)

    try:
        yield SessionFactory
    finally:
        outer_tx.rollback()
        connection.close()


# @pytest.fixture()
# def uow_factory(db_session):
#     # fresh UoW per test
#     return lambda: SQLAlchemyConversationUOW(db_session)
