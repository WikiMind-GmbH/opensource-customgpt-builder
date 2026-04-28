from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)


class QdrantVectorStoreTextChunks(VectorStorePortTextChunks):
    def __init__(self, db_url: str) -> None:
        self.client = QdrantClient(url=db_url)
        self.client.create_collection(
            collection_name="TextChunksCollection",
            vectors_config=VectorParams(size=100, distance=Distance.COSINE),
        )
