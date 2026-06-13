from collections.abc import Generator

import pytest
from qdrant_client import QdrantClient
from sqlalchemy import (
    Connection,
    Engine,
    NullPool,
    RootTransaction,
    create_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.infrastructure.adapters.embedding_generator_openai_adapter import (
    EmbeddingGeneratorOpenAIAdapter,
)
from src.contexts.knowledge.infrastructure.adapters.qdrant_vector_store_adapter import (
    QdrantVectorStoreTextChunksAdapter,
)
from src.contexts.knowledge.infrastructure.db.orm import metadata as knowledge_metadata


@pytest.fixture(scope="session")
def engine(start_knowledge_mappers: None) -> Generator[Engine, None, None]:
    eng = create_engine(
        require_env("DB_URL_KNOWLEDGE_TEST"), poolclass=NullPool
    )  # No connection pooling
    knowledge_metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine: Engine) -> Generator[sessionmaker[Session], None, None]:
    """
    Provides a sessionmaker that creates NEW sessions, all bound to the same
    connection+outer transaction for this test.
    """
    connection: Connection = engine.connect()
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


# def upload_document_complete_workflow_return_file_id(
#     file_bytes_content: bytes,
#     file_name_with_ending: str,
#     extract_text_from_document_adapter: ExtractTextFromDocumentPort,
#     knowledge_uow_factory: Factory[KnowledgeUOW],
#     accessible_to_cgpts: list[str],
#     cgpt_permissions_adapter: CgptPermissionCheckerPort,
#     knowledge_db_queries_adapter: KnowledgeDBQueriesPort,
#     file_storage_adapter: RawFileStorePort,
#     background_tasks: BackgroundTasks,
# ) -> UUID:


@pytest.fixture()
def embedding_generator() -> EmbeddingGeneratorPort:
    embedding_generator = EmbeddingGeneratorOpenAIAdapter()
    return embedding_generator


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
