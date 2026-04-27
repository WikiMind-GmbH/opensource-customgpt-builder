from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.contexts.knowledge.domain.models import TextFileChunk


class NotFoundError(RuntimeError):
    "This object does not exist"


@dataclass
class AddChunkEmbeddingsDTO:
    file_id: str
    id_and_embedding_pairs_of_chunks: list[tuple[str, list[float]]]


class VectorStorePortTextChunks(Protocol):
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
