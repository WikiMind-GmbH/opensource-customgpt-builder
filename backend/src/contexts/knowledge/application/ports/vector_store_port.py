from __future__ import annotations

from typing import Protocol

from src.contexts.knowledge.domain.models import TextFileChunk


class NotFoundError(RuntimeError):
    "This object does not exist"


class VectorStorePortTextChunks(Protocol):
    def return_relevant_text_snippets(
        self,
        file_ids: list[str],
        max_snippets: int = 5,
    ) -> list[TextFileChunk]: ...
    def add_chunk_with_embedding(
        self, chunk: TextFileChunk, embedding_vector: list[float]
    ) -> None: ...
