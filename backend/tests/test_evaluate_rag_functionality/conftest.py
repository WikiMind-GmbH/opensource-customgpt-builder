# from __future__ import annotations
from typing import Generator

import pytest
from qdrant_client import QdrantClient
from sqlalchemy import Connection, Engine, NullPool, RootTransaction, create_engine
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata
from src.contexts.chat.infrastructure.db.orm import start_mappers as chat_start
from src.contexts.chat.infrastructure.db.uow_implementations import (
    SQLAlchemyConversationUOW,
)
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.infrastructure.adapters.retreive_instructions import (
    CustomGPTInstructionsRetreiverAdapter,
)
from src.contexts.customGPTs.infrastructure.db.orm import metadata as cgpt_metadata
from src.contexts.customGPTs.infrastructure.db.orm import start_mappers as cgpt_start
from src.contexts.customGPTs.infrastructure.db.uow_implementations import (
    SQLAlchemyCgptUOW,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.infrastructure.adapters.embedding_generator_openai_adapter import (
    EmbeddingGeneratorOpenAIAdapter,
)
from src.contexts.knowledge.infrastructure.adapters.qdrant_vector_store_adapter import (
    QdrantVectorStoreTextChunksAdapter,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    start_mappers as knowledge_start,
)
from src.contexts.shared.typing_aliases import Factory


@pytest.fixture(scope="session")
def start_cgpt_mappers() -> Generator[None, None, None]:
    cgpt_start()
    yield


@pytest.fixture(scope="session")
def start_chat_mappers() -> Generator[None, None, None]:
    chat_start()
    yield


@pytest.fixture(scope="session")
def start_knowledge_mappers() -> Generator[None, None, None]:
    knowledge_start()
    yield


@pytest.fixture(scope="session", autouse=True)
def _clear_mappers_at_end() -> Generator[None, None, None]:  # pyright: ignore [reportUnusedFunction] ; REASON: autoUUse=True -> function means function is used
    # not autouse? then just depend on it from a top-level fixture
    yield
    clear_mappers()


@pytest.fixture()
def fresh_qdrant_vector_store_adapter() -> Generator[
    QdrantVectorStoreTextChunksAdapter
]:
    db_url = require_env("QDRANT_URL")
    vector_store_adapter: QdrantVectorStoreTextChunksAdapter = (
        QdrantVectorStoreTextChunksAdapter(
            db_url=db_url,
            embedding_dimension=2,
            create_adapter_for_testing_with_test_collection=True,
        )
    )
    collection_name = vector_store_adapter.collection_name

    try:
        yield vector_store_adapter
        vector_store_adapter.close_client()

    finally:
        collection_name = vector_store_adapter.collection_name
        clean_up_client = QdrantClient(url=db_url)
        clean_up_client.delete_collection(collection_name=collection_name)
        clean_up_client.close()


# --------------  ConversationUOW  -----------------


@pytest.fixture()
def conv_engine(start_chat_mappers: None) -> Generator[Engine, None, None]:
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


# # --------------  CustomGPTInstructionsRetreiver  -----------------


@pytest.fixture()
def cgpt_engine(start_cgpt_mappers: None) -> Generator[Engine, None, None]:
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
def embedding_generator() -> EmbeddingGeneratorPort:
    embedding_generator = EmbeddingGeneratorOpenAIAdapter()
    return embedding_generator
