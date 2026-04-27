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

    def return_relevant_text_snippets(
        self,
        file_ids: list[str],
        max_snippets: int = 5,
    ) -> list[TextFileChunk]: ...
    def add_chunk_with_embedding(
        self, chunk: TextFileChunk, embedding_vector: list[float]
    ) -> None: ...

    def get_metadata_of_chunk(self, id_of_chunk: str) -> str: ...
    def change_metadata_of_chunk(
        self, id_of_chunk: str, new_metadata: dict[str, str]
    ) -> None: ...
