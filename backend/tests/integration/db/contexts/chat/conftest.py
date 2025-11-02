from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import prepare_engine
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest



@pytest.fixture()
def engine(start_chat_mappers):
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

# @pytest.fixture()
# def uow_factory(db_session):
#     # fresh UoW per test
#     return lambda: SQLAlchemyConversationUOW(db_session)
