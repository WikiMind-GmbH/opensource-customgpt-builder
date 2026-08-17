from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import (
    Connection,
    Engine,
    NullPool,
    RootTransaction,
    create_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from backend_spanning_helpers import require_env
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    ExtractTextFromDocumentPort,
)
from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.infrastructure.adapters.extract_text_from_document_adapter import (
    ExtractTextFromDocumentsAdapter,
)
from src.contexts.knowledge.infrastructure.adapters.local_file_system_storage_adapter import (
    RawFileStoreLocalFsAdapter,
)
from src.contexts.knowledge.infrastructure.db.knowledge_uow_adapter import (
    SQLAlchemyKnowledgeUOW,
)
from src.contexts.knowledge.infrastructure.db.orm import metadata as knowledge_metadata
from tests.documents_for_tests.test_documents import AvailableFiles, TestDocuments
from tests.fake_adapters.context_knowledge_port.fake_cgpt_permission_checker import (
    FakeCgptPermissionChecker,
)
from tests.fake_adapters.context_knowledge_port.fake_embedding_generator import (
    DeterministicEmbeddingGeneratorAdapter,
)
from tests.fake_adapters.context_knowledge_port.fake_task_scheduler import (
    FakeTaskScheduler,
)
from tests.fake_adapters.context_knowledge_port.fake_vector_store import (
    FakeVectorStoreTextChunksAdapter,
)


@pytest.fixture()
def embedding_dimension() -> int:
    embedding_dimension = 10
    return embedding_dimension


# We will use fakes for everything except for the domain orm mapped database
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


@pytest.fixture()
def knowledge_uow_factory(session_factory: sessionmaker[Session]):
    return lambda: SQLAlchemyKnowledgeUOW(session_factory=session_factory)


@pytest.fixture()
def fake_embedding_generator(embedding_dimension: int) -> EmbeddingGeneratorPort:
    generator = DeterministicEmbeddingGeneratorAdapter(
        embedding_dimension=embedding_dimension
    )
    return generator


@pytest.fixture()
def fake_vector_store(embedding_dimension: int) -> VectorStorePortTextChunks:
    return FakeVectorStoreTextChunksAdapter(embedding_dimension=embedding_dimension)


@pytest.fixture()
def extract_text_from_document_adapter() -> ExtractTextFromDocumentPort:
    return ExtractTextFromDocumentsAdapter()


@pytest.fixture()
def file_store(tmp_path: Path) -> RawFileStoreLocalFsAdapter:
    # pytest's built-in tmp_path fixture provides a unique temporary directory
    # per test and cleans it up automatically.

    return RawFileStoreLocalFsAdapter(file_storage_folder=tmp_path)


@pytest.fixture()
def fake_task_scheduler() -> FakeTaskScheduler:
    return FakeTaskScheduler()


@pytest.fixture()
def cgpt_permission_checker_true_return() -> CgptPermissionCheckerPort:
    return FakeCgptPermissionChecker(will_raise_error=False)


@pytest.fixture()
def cgpt_permission_checker_false_return() -> CgptPermissionCheckerPort:
    return FakeCgptPermissionChecker(will_raise_error=True)


@pytest.fixture()
def fabricated_text_document_bytes() -> bytes:
    path = TestDocuments.get_paths_for_test_files(file=AvailableFiles.aurelian)
    with open(path, "rb") as contents:
        return contents.read()
