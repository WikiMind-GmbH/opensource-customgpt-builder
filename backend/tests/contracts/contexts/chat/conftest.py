from src.contexts.chat.infrastructure.db.conv_repo_implmementations import SQAlchemyConversartionRepository
from src.contexts.chat.infrastructure.adapters.chat_queries_sqlalchemy import ChatQueriesAdapter
from src.contexts.chat.infrastructure.db.orm import metadata
from src.contexts.shared.typing_aliases import Factory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import pytest


@pytest.fixture()
def engine(start_chat_mappers):
    eng = create_engine("sqlite:///:memory:")
    metadata.create_all(eng)
    yield eng
    eng.dispose()

@pytest.fixture()
def session_factory(engine):
    SessionFactory = sessionmaker(engine, expire_on_commit=False)
    return SessionFactory

@pytest.fixture()
def sqla_conv_repo_factory(session_factory: Factory[Session]):
    return lambda: SQAlchemyConversartionRepository(session=session_factory())



@pytest.fixture()
def chat_query_factory(session_factory: Factory[Session])-> Factory[ChatQueriesAdapter]:
    # fresh UoW per test
    return lambda: ChatQueriesAdapter(chat_session_factory = session_factory)

@pytest.fixture()
def adapter(chat_query_factory:Factory[ChatQueriesAdapter]) -> ChatQueriesAdapter:
    return chat_query_factory()