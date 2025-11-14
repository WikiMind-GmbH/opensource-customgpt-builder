from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.infrastructure.adapters.conv_adapter import ConversationAdapter
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.uow_implementations import SQLAlchemyConversationUOW
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.infrastructure.db.uow_implementations import SQLAlchemyCgptUOW
from src.contexts.shared.typing_aliases import Factory
from src.contexts.customGPTs.infrastructure.db.orm import metadata
from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, Session
import pytest

from src.contexts.chat.infrastructure.db.orm import (
    prepare_engine,
)
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata
# --------------  CustomGPT UOW  -----------------

@pytest.fixture()
def engine(start_cgpt_mappers):
    eng = create_engine("sqlite:///:memory:")
    metadata.create_all(eng)
    yield eng
    eng.dispose()

@pytest.fixture()
def session_factory(engine)-> Factory[Session]:
    SessionFactory = sessionmaker(engine, expire_on_commit=False)
    return SessionFactory

@pytest.fixture()
def cgpt_uow_factory(session_factory: Factory[Session]) -> Factory[CgptUOW]:
    return lambda: SQLAlchemyCgptUOW(session_factory=session_factory)

# --------------  ConversationUOW  -----------------


@pytest.fixture()
def conv_engine(start_chat_mappers):
    eng = create_engine("sqlite:///:memory:")
    eng = prepare_engine(eng)
    chat_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def conv_session_factory(conv_engine):
    SessionFactory = sessionmaker(conv_engine, expire_on_commit=False)
    register_last_message_at_events(SessionFactory)
    return SessionFactory


@pytest.fixture()
def conv_uow_factory(conv_session_factory):
    return lambda: SQLAlchemyConversationUOW(session_factory=conv_session_factory)

@pytest.fixture()
def conversation_adapter_factory(conv_uow_factory: Factory[ConversationUOW])-> Factory[ConversationPort]:
    return lambda: ConversationAdapter(conv_uow_factory=conv_uow_factory)