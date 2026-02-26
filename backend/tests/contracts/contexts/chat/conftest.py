from collections.abc import Generator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.contexts.chat.infrastructure.adapters.chat_queries_sqlalchemy import (
    ChatQueriesAdapter,
)
from src.contexts.chat.infrastructure.db.conv_repo_implmementations import (
    SQAlchemyConversartionRepository,
)
from src.contexts.chat.infrastructure.db.orm import metadata
from src.contexts.shared.typing_aliases import Factory


@pytest.fixture()
def engine(start_chat_mappers: None) -> Generator[Engine, None, None]:
    eng = create_engine("sqlite:///:memory:")
    metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine: Engine) -> sessionmaker[Session]:
    SessionFactory = sessionmaker(
        engine,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    return SessionFactory


@pytest.fixture()
def sqla_conv_repo_factory(session_factory: sessionmaker[Session]):
    return lambda: SQAlchemyConversartionRepository(session=session_factory())


@pytest.fixture()
def chat_query_factory(
    session_factory: sessionmaker[Session],
) -> Factory[ChatQueriesAdapter]:
    # fresh UoW per test
    return lambda: ChatQueriesAdapter(chat_session_factory=session_factory)


@pytest.fixture()
def adapter(chat_query_factory: Factory[ChatQueriesAdapter]) -> ChatQueriesAdapter:
    return chat_query_factory()
