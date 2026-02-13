import pytest
from sqlalchemy import Connection, NullPool, RootTransaction, create_engine
from sqlalchemy.orm import sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.customGPTs.infrastructure.db.orm import metadata as cgpt_metadata


@pytest.fixture()
def engine(start_cgpt_mappers):
    eng = create_engine(
        require_env("DB_URL_CGPT_TEST"), poolclass=NullPool
    )  # No connection pooling
    cgpt_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine):
    """
    Provides a sessionmaker that creates NEW sessions, all bound to the same
    connection+outer transaction for this test.
    """
    connection: Connection = engine.connect()
    outer_tx: RootTransaction = connection.begin()

    SessionFactory = sessionmaker(bind=connection, expire_on_commit=False)

    try:
        yield SessionFactory
    finally:
        outer_tx.rollback()
        connection.close()
