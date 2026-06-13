from collections.abc import Generator
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient
from sqlalchemy import Connection, NullPool, RootTransaction, create_engine
from sqlalchemy.orm import sessionmaker

from backend_spanning_helpers import require_env
from src.bootstrap import (
    DependenciesContainer,
    SQLDBResource,
    SQLDBResourceOfContexts,
    create_dependencies,
)
from src.contexts.chat.infrastructure.db.events import register_last_message_at_events
from src.contexts.chat.infrastructure.db.orm import metadata as chat_metadata
from src.contexts.customGPTs.infrastructure.db.orm import metadata as cgpt_metadata
from src.contexts.knowledge.infrastructure.db.orm import metadata as knowledge_metadata
from tests.fake_adapters.context_chat_port.fake_llm_adapter import FakeLLMAdapter


@pytest.fixture()
def sql_db_resources_of_contexts() -> Generator[SQLDBResourceOfContexts, None, None]:
    chat_engine = create_engine(require_env("DB_URL_CHAT_TEST"), poolclass=NullPool)
    cgpt_engine = create_engine(require_env("DB_URL_CGPT_TEST"), poolclass=NullPool)
    knowledge_engine = create_engine(
        require_env("DB_URL_KNOWLEDGE_TEST"),
        poolclass=NullPool,
    )

    chat_metadata.create_all(chat_engine)
    cgpt_metadata.create_all(cgpt_engine)
    knowledge_metadata.create_all(knowledge_engine)

    chat_connection: Connection = chat_engine.connect()
    cgpt_connection: Connection = cgpt_engine.connect()
    knowledge_connection: Connection = knowledge_engine.connect()

    chat_outer_tx: RootTransaction = chat_connection.begin()
    cgpt_outer_tx: RootTransaction = cgpt_connection.begin()
    knowledge_outer_tx: RootTransaction = knowledge_connection.begin()

    chat_session_factory = sessionmaker(
        bind=chat_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    cgpt_session_factory = sessionmaker(
        bind=cgpt_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    knowledge_session_factory = sessionmaker(
        bind=knowledge_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    register_last_message_at_events(chat_session_factory)

    sql_db_resources = SQLDBResourceOfContexts(
        chat_resources=SQLDBResource(
            engine=chat_engine,
            session_factory=chat_session_factory,
        ),
        cgpt_resources=SQLDBResource(
            engine=cgpt_engine,
            session_factory=cgpt_session_factory,
        ),
        knowledge_resources=SQLDBResource(
            engine=knowledge_engine,
            session_factory=knowledge_session_factory,
        ),
    )

    try:
        yield sql_db_resources
    finally:
        knowledge_outer_tx.rollback()
        cgpt_outer_tx.rollback()
        chat_outer_tx.rollback()

        knowledge_connection.close()
        cgpt_connection.close()
        chat_connection.close()

        knowledge_engine.dispose()
        cgpt_engine.dispose()
        chat_engine.dispose()


@pytest.fixture()
def test_dependencies_container(
    sql_db_resources_of_contexts: SQLDBResourceOfContexts,
) -> Generator[DependenciesContainer, None, None]:
    db_url_vectorstore = require_env("QDRANT_URL")

    dependencies = create_dependencies(
        sql_db_resources_of_contexts=sql_db_resources_of_contexts,
        model_name="fake-model",
        vector_store_is_for_testing=True,
        db_url_vectorstore=db_url_vectorstore,
    )

    collection_name = dependencies.vector_store_adapter_factory().collection_name

    test_dependencies = replace(
        dependencies,
        llm_adapter_factory=lambda: FakeLLMAdapter(),
    )

    try:
        yield test_dependencies
    finally:
        clean_up_client = QdrantClient(url=db_url_vectorstore)
        try:
            if clean_up_client.collection_exists(collection_name):
                clean_up_client.delete_collection(collection_name=collection_name)
        finally:
            clean_up_client.close()


@pytest.fixture()
def test_client_fake_adapters(
    test_dependencies_container: DependenciesContainer,
) -> Generator[TestClient, None, None]:
    from src.interface.http.app import app
    from src.interface.http.composition import dependencies_container

    original_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[
        dependencies_container.conversation_uow_factory_factory
    ] = test_dependencies_container.conversation_uow_factory_factory

    app.dependency_overrides[dependencies_container.cgpt_uow_factory_factory] = (
        test_dependencies_container.cgpt_uow_factory_factory
    )

    app.dependency_overrides[dependencies_container.cgpt_retreiver_adapter_factory] = (
        test_dependencies_container.cgpt_retreiver_adapter_factory
    )

    app.dependency_overrides[dependencies_container.llm_adapter_factory] = (
        test_dependencies_container.llm_adapter_factory
    )

    app.dependency_overrides[dependencies_container.cgpt_queries_adapter_factory] = (
        test_dependencies_container.cgpt_queries_adapter_factory
    )

    app.dependency_overrides[dependencies_container.chat_queries_adapter_factory] = (
        test_dependencies_container.chat_queries_adapter_factory
    )

    app.dependency_overrides[dependencies_container.conversation_adapter_factory] = (
        test_dependencies_container.conversation_adapter_factory
    )

    app.dependency_overrides[dependencies_container.knowledge_uow_factory_factory] = (
        test_dependencies_container.knowledge_uow_factory_factory
    )

    app.dependency_overrides[
        dependencies_container.cgpt_permissions_adapter_factory
    ] = test_dependencies_container.cgpt_permissions_adapter_factory

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides = original_overrides
