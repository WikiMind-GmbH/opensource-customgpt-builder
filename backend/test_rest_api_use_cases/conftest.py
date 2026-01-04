import os
from fastapi.testclient import TestClient
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.infrastructure.adapters.conv_adapter import ConversationAdapter
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort
from src.contexts.chat.infrastructure.adapters.chat_queries_sqlalchemy import (
    ChatQueriesAdapter,
)
from src.contexts.customGPTs.infrastructure.adapters.cgpt_queries import (
    CgptQueriesImplementation,
)
from src.bootstrap import DependenciesContainer

import pytest

# from __future__ import annotations

from test_rest_api_use_cases.FakeAdapters import FakeLLMAdapter

from src.contexts.chat.application.ports.llm_port import LlmPort
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.infrastructure.adapters.retreive_instructions import (
    CustomGPTInstructionsRetreiverAdapter,
)
from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.shared.typing_aliases import Factory
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import (
    prepare_engine,
)
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata

from src.contexts.customGPTs.infrastructure.db.orm import metadata as cgpt_metadata
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

import pytest


# # --------------  ConversationUOW  -----------------


@pytest.fixture() 
def conv_engine(): # importing app <- importst deps <- runs bootstrap <- runs mappers : No mapping possible/needed
    eng = create_engine("sqlite:///test-conv.db")
    eng = prepare_engine(eng)
    chat_metadata.create_all(eng)
    try:
        yield eng
        eng.dispose()
    finally:
        os.remove("test-conv.db")


@pytest.fixture()
def conv_session_factory(conv_engine):
    SessionFactory = sessionmaker(conv_engine, expire_on_commit=False)
    register_last_message_at_events(SessionFactory)
    return SessionFactory


@pytest.fixture()
def conv_uow_factory(conv_session_factory):
    return lambda: SQLAlchemyConversationUOW(session_factory=conv_session_factory)


@pytest.fixture()
def chat_query_factory(
    conv_session_factory: Factory[Session],
) -> Factory[ChatQueriesAdapter]:
    return lambda: ChatQueriesAdapter(chat_session_factory=conv_session_factory)

@pytest.fixture()
def conversation_adapter_factory(conv_uow_factory: Factory[ConversationUOW])-> Factory[ConversationPort]:
    return lambda: ConversationAdapter(conv_uow_factory=conv_uow_factory)


# # --------------  CustomGPTInstructionsRetreiver  -----------------


@pytest.fixture()
def cgpt_engine(): # importing app <- importst deps <- runs bootstrap <- runs mappers : No mapping possible/needed
    eng = create_engine("sqlite:///test-cgpt.db")
    cgpt_metadata.create_all(eng)
    try:
        yield eng
        eng.dispose()
    finally:
        os.remove("test-cgpt.db")


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


@pytest.fixture()
def cgpt_query_factory(
    cgpt_session_factory: Factory[Session],
) -> Factory[CgptQueriesImplementation]:
    return lambda: CgptQueriesImplementation(cgpt_session_factory=cgpt_session_factory)


# --------------  LLM Adapter  -----------------


@pytest.fixture()
def fake_llm_adapter_factory() -> Factory[FakeLLMAdapter]:
    return lambda: FakeLLMAdapter()


@pytest.fixture()
def test_deps(
    conv_uow_factory,
    cgpt_uow_factory,
    cgpt_retreiver_factory,
    fake_llm_adapter_factory,
    cgpt_query_factory,
    chat_query_factory,
    conversation_adapter_factory,
)->DependenciesContainer:
    test_deps_container: DependenciesContainer = DependenciesContainer(
        conversation_uow_factory=conv_uow_factory,
        cgpt_uow_factory=cgpt_uow_factory,
        cgpt_retreiver_adapter_factory=cgpt_retreiver_factory,
        llm_adapter_factory=fake_llm_adapter_factory,
        cgpt_queries_adapter_factory=cgpt_query_factory,
        chat_queries_adapter_factory=chat_query_factory,
        conversation_adapter_factory=conversation_adapter_factory,
    )
    return test_deps_container


@pytest.fixture()
def test_client(test_deps:DependenciesContainer):
    from backend.src.interface.http.composition import dependencies_container
    from src.interface.http.app import app
    app.dependency_overrides[dependencies_container.conversation_uow_factory] = test_deps.conversation_uow_factory
    app.dependency_overrides[dependencies_container.cgpt_uow_factory] = test_deps.cgpt_uow_factory
    app.dependency_overrides[dependencies_container.cgpt_retreiver_adapter_factory] = test_deps.cgpt_retreiver_adapter_factory
    app.dependency_overrides[dependencies_container.llm_adapter_factory] = test_deps.llm_adapter_factory
    app.dependency_overrides[dependencies_container.cgpt_queries_adapter_factory] = test_deps.cgpt_queries_adapter_factory
    app.dependency_overrides[dependencies_container.chat_queries_adapter_factory] = test_deps.chat_queries_adapter_factory
    app.dependency_overrides[dependencies_container.conversation_adapter_factory] = test_deps.conversation_adapter_factory
    test_app: TestClient = TestClient(app)
    return test_app


# @pytest.fixture()
# def test_client(
#     conv_uow_factory,
#     cgpt_uow_factory,
#     cgpt_retreiver_factory,
#     fake_llm_adapter_factory,
#     cgpt_query_factory,
#     chat_query_factory,
# )->TestClient:
#     from src.interface.http.deps import deps
#     from src.interface.http.app import app
#     app.dependency_overrides[deps.conversation_uow_factory] = conv_uow_factory
#     app.dependency_overrides[deps.cgpt_uow_factory] = cgpt_uow_factory
#     app.dependency_overrides[deps.cgpt_retreiver_adapter_factory] = cgpt_retreiver_factory
#     app.dependency_overrides[deps.llm_adapter_factory] = fake_llm_adapter_factory
#     app.dependency_overrides[deps.cgpt_queries_adapter_factory] = cgpt_query_factory
#     app.dependency_overrides[deps.chat_queries_adapter_factory] = chat_query_factory
#     test_app: TestClient = TestClient(app)
#     return test_app