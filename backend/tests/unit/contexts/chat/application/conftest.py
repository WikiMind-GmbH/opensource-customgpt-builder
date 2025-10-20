from src.contexts.chat.infrastructure.db.uow_implementations import SQLAlchemyConversationUOW
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import prepare_engine, start_mappers as start_mappers_chat
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, clear_mappers
import pytest

# If the below leads to errors, consider refactoring with the following:
@pytest.fixture(scope="session")
def mappers():
    start_mappers_chat()
    yield
    clear_mappers() # Can't call start_mappers multiple times in same runtime! (without this)

@pytest.fixture()
def engine(mappers):
    eng = create_engine("sqlite:///:memory:")
    eng = prepare_engine(eng)
    chat_metadata.create_all(eng)
    yield eng
    eng.dispose()

@pytest.fixture()
def session_factory(engine):
    SessionFactory = sessionmaker(engine, expire_on_commit=False)
    register_last_message_at_events(SessionFactory)
    return SessionFactory

@pytest.fixture()
def uow_factory(db_session):
    # fresh UoW per test
    return lambda: SQLAlchemyConversationUOW(db_session)