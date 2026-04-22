from collections.abc import Generator

import pytest
from sqlalchemy import (
    Connection,
    Engine,
    NullPool,
    RootTransaction,
    create_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.knowledge.infrastructure.db.orm import metadata as knowledge_metadata


@pytest.fixture(scope="session")
def engine(start_knowledge_mappers: None) -> Generator[Engine, None, None]:
    eng = create_engine(
        require_env("DB_URL_KNOWLEDGE_TEST"), poolclass=NullPool
    )  # No connection pooling
    knowledge_metadata.create_all(eng)
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

    SessionFactory = sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield SessionFactory
    finally:
        outer_tx.rollback()
        connection.close()
