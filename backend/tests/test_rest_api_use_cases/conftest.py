from collections.abc import Generator, Iterator
from contextlib import contextmanager
from dataclasses import fields, replace

import pytest
from fastapi import FastAPI
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
def test_sql_db_resources_of_contexts() -> Generator[
    SQLDBResourceOfContexts, None, None
]:
    """
    Do not use the production DB bootstrap here.

    Tests need connection-bound session factories and outer transactions so app
    code can call commit() normally while the fixture rolls everything back
    afterwards.

    The production bootstrap creates engine-bound session factories and does not
    expose the connection/transaction lifecycle needed for test isolation.
    """
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
def original_dependencies_container_but_with_test_databases(
    test_sql_db_resources_of_contexts: SQLDBResourceOfContexts,
) -> Generator[DependenciesContainer, None, None]:
    db_url_vectorstore = require_env("QDRANT_URL")

    original_dependencies_container_but_with_test_databases = create_dependencies(
        sql_db_resources_of_contexts=test_sql_db_resources_of_contexts,
        vector_store_is_for_testing=True,
    )

    collection_name = original_dependencies_container_but_with_test_databases.vector_store_adapter_factory().collection_name

    try:
        yield original_dependencies_container_but_with_test_databases
    finally:
        clean_up_client = QdrantClient(url=db_url_vectorstore)
        try:
            if clean_up_client.collection_exists(collection_name):
                clean_up_client.delete_collection(collection_name=collection_name)
        finally:
            clean_up_client.close()


@contextmanager
def override_all_app_deps_with(
    *,
    app: FastAPI,
    dependency_overrides_source: DependenciesContainer,
) -> Iterator[FastAPI]:
    from src.interface.http.composition import dependencies_container

    original_overrides = app.dependency_overrides.copy()

    try:
        app.dependency_overrides.update(
            {
                getattr(dependencies_container, field.name): getattr(
                    dependency_overrides_source,
                    field.name,
                )
                for field in fields(DependenciesContainer)
            }
        )

        yield app

    finally:
        app.dependency_overrides = original_overrides


@pytest.fixture()
def test_client_fake_llm_adapter(
    original_dependencies_container_but_with_test_databases: DependenciesContainer,
) -> Generator[TestClient, None, None]:
    from src.interface.http.app import app

    deps_with_test_dbs_and_fake_llm: DependenciesContainer = replace(
        original_dependencies_container_but_with_test_databases,
        llm_adapter_factory=lambda: FakeLLMAdapter(),
    )

    with override_all_app_deps_with(
        app=app,
        dependency_overrides_source=deps_with_test_dbs_and_fake_llm,
    ) as test_app:
        with TestClient(test_app) as test_client:
            yield test_client


@pytest.fixture()
def test_client_real_adapters(
    original_dependencies_container_but_with_test_databases: DependenciesContainer,
) -> Generator[TestClient, None, None]:
    from src.interface.http.app import app

    with override_all_app_deps_with(
        app=app,
        dependency_overrides_source=original_dependencies_container_but_with_test_databases,
    ) as test_app:
        with TestClient(test_app) as test_client:
            yield test_client
