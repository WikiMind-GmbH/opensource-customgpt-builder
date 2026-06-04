from typing import Generator

import pytest
from qdrant_client import QdrantClient

from backend_spanning_helpers import require_env
from src.contexts.knowledge.infrastructure.adapters.vector_store_adapter import (
    QdrantVectorStoreTextChunksAdapter,
)


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
