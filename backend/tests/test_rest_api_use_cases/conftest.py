from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, NullPool, RootTransaction, create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend_spanning_helpers import require_env
from src.bootstrap import DependenciesContainer
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.infrastructure.adapters.chat_queries_sqlalchemy import (
    ChatQueriesAdapter,
)
from src.contexts.chat.infrastructure.adapters.conv_adapter import ConversationAdapter
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.infrastructure.adapters.cgpt_queries import (
    CgptQueriesImplementation,
)
from src.contexts.customGPTs.infrastructure.adapters.retreive_instructions import (
    CustomGPTInstructionsRetreiverAdapter,
)
from src.contexts.customGPTs.infrastructure.db.orm import metadata as cgpt_metadata
from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.shared.typing_aliases import Factory
from tests.fake_adapters.context_chat.fake_llm_adapter import FakeLLMAdapter

# from __future__ import annotations

# # --------------  ConversationUOW  -----------------


@pytest.fixture()
def conv_engine() -> (
    Generator[Engine, None, None]
):  # importing app <- importst deps <- runs bootstrap <- runs mappers : No mapping possible/needed
    eng = create_engine(
        require_env("DB_URL_CHAT_TEST"), poolclass=NullPool
    )  # No connection pooling
    chat_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def conv_session_factory(
    conv_engine: Engine,
) -> Generator[sessionmaker[Session], None, None]:
    """
    Provides a sessionmaker that creates NEW sessions, all bound to the same
    connection+outer transaction for this test.
    """
    connection: Connection = conv_engine.connect()
    outer_tx: RootTransaction = connection.begin()

    SessionFactory = sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    register_last_message_at_events(SessionFactory)

    try:
        yield SessionFactory
    finally:
        outer_tx.rollback()
        connection.close()


@pytest.fixture()
def conv_uow_factory(
    conv_session_factory: sessionmaker[Session],
) -> Factory[SQLAlchemyConversationUOW]:
    return lambda: SQLAlchemyConversationUOW(session_factory=conv_session_factory)


@pytest.fixture()
def chat_query_factory(
    conv_session_factory: sessionmaker[Session],
) -> Factory[ChatQueriesAdapter]:
    return lambda: ChatQueriesAdapter(chat_session_factory=conv_session_factory)


@pytest.fixture()
def conversation_adapter_factory(
    conv_uow_factory: Factory[ConversationUOW],
) -> Factory[ConversationPort]:
    return lambda: ConversationAdapter(conv_uow_factory=conv_uow_factory)


# # --------------  CustomGPTInstructionsRetreiver  -----------------


@pytest.fixture()
def cgpt_engine() -> (
    Generator[Engine, None, None]
):  # importing app <- importst deps <- runs bootstrap <- runs mappers : No mapping possible/needed
    eng = create_engine(
        require_env("DB_URL_CGPT_TEST"), poolclass=NullPool
    )  # No connection pooling
    cgpt_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def cgpt_session_factory(
    cgpt_engine: Engine,
) -> Generator[sessionmaker[Session], None, None]:
    """
    Provides a sessionmaker that creates NEW sessions, all bound to the same
    connection+outer transaction for this test.
    """
    connection: Connection = cgpt_engine.connect()
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


@pytest.fixture()
def cgpt_uow_factory(cgpt_session_factory: sessionmaker[Session]) -> Factory[CgptUOW]:
    return lambda: SQLAlchemyCgptUOW(session_factory=cgpt_session_factory)


@pytest.fixture()
def cgpt_retreiver_factory(
    cgpt_uow_factory: Factory[CgptUOW],
) -> Factory[CustomGPTInstructionsRetreiverAdapter]:
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
    conv_uow_factory: Factory[ConversationUOW],
    cgpt_uow_factory: Factory[CgptUOW],
    cgpt_retreiver_factory: Factory[CustomGPTInstructionsRetreiverAdapter],
    fake_llm_adapter_factory: Factory[FakeLLMAdapter],
    cgpt_query_factory: Factory[CgptQueriesImplementation],
    chat_query_factory: Factory[ChatQueriesAdapter],
    conversation_adapter_factory: Factory[ConversationPort],
) -> DependenciesContainer:
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
def test_client(test_deps: DependenciesContainer):
    from src.interface.http.app import app
    from src.interface.http.composition import dependencies_container

    app.dependency_overrides[dependencies_container.conversation_uow_factory] = (
        test_deps.conversation_uow_factory
    )
    app.dependency_overrides[dependencies_container.cgpt_uow_factory] = (
        test_deps.cgpt_uow_factory
    )
    app.dependency_overrides[dependencies_container.cgpt_retreiver_adapter_factory] = (
        test_deps.cgpt_retreiver_adapter_factory
    )
    app.dependency_overrides[dependencies_container.llm_adapter_factory] = (
        test_deps.llm_adapter_factory
    )
    app.dependency_overrides[dependencies_container.cgpt_queries_adapter_factory] = (
        test_deps.cgpt_queries_adapter_factory
    )
    app.dependency_overrides[dependencies_container.chat_queries_adapter_factory] = (
        test_deps.chat_queries_adapter_factory
    )
    app.dependency_overrides[dependencies_container.conversation_adapter_factory] = (
        test_deps.conversation_adapter_factory
    )
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
