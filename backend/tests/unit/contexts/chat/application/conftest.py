# from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata
from src.contexts.chat.infrastructure.db.orm import (
    prepare_engine,
)
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.infrastructure.adapters.retreive_instructions import (
    CustomGPTInstructionsRetreiverAdapter,
)
from src.contexts.customGPTs.infrastructure.db.orm import metadata as cgpt_metadata
from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.shared.typing_aliases import Factory
from tests.unit.contexts.chat.application.FakeAdapters import FakeLLMAdapter

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


# # --------------  CustomGPTInstructionsRetreiver  -----------------


@pytest.fixture()
def cgpt_engine(start_cgpt_mappers):
    eng = create_engine("sqlite:///:memory:")
    cgpt_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def cgpt_session_factory(cgpt_engine) -> Factory[Session]:
    SessionFactory = sessionmaker(cgpt_engine, expire_on_commit=False)
    return SessionFactory


@pytest.fixture()
def cgpt_uow_factory(cgpt_session_factory: Factory[Session]) -> Factory[CgptUOW]:
    return lambda: SQLAlchemyCgptUOW(session_factory=cgpt_session_factory)


@pytest.fixture()
def cgpt_retreiver_factory(cgpt_uow_factory: Factory[CgptUOW]):
    return lambda: CustomGPTInstructionsRetreiverAdapter(
        cgpt_uow_factory=cgpt_uow_factory
    )


# --------------  LLM Adapter  -----------------


@pytest.fixture()
def fake_llm_adapter_factory() -> Factory[FakeLLMAdapter]:
    return lambda: FakeLLMAdapter()
