from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class NotFoundError(RuntimeError):
    "This object does not exist"


class InvalidEmbeddingDimension(RuntimeError):
    "The embedding dimension of passed vectors must match the one of the vevctorstore"


class ParentOrChildDTO(StrEnum):
    parent = "parent"
    child = "child"


@dataclass
class MetadataDTO:
    parent_or_child_chunk: ParentOrChildDTO
    id_of_corresponding_file: str
    text_content: str


@dataclass
class ChunkEmbeddingAndMetadataDTO:
    embedding_vector: list[float]
    metadata: MetadataDTO
    id_of_chunk: str


@dataclass
class TextChunkReturnDTO:
    id_of_chunk: str
    score: float


class VectorStorePortTextChunks(Protocol):
    @property
    def embedding_dimension(self) -> int:
        """Dimension expected of the vector store in its collections"""
        ...

    def return_relevant_text_snippets_ids_and_text(
        self,
        embedding_to_match: list[float],
        file_ids_to_include_in_filter: list[str],
        max_snippets: int = 5,
        include_only_parent_or_child_chunks: ParentOrChildDTO | None = None,
    ) -> list[TextChunkReturnDTO]: ...

    def add_chunks_with_corresponding_embeddings_and_metadata(
        self, chunk_embeddings_and_metadata_dtos: list[ChunkEmbeddingAndMetadataDTO]
    ) -> None: ...

    def get_metadata_of_chunk(self, id_of_chunk: str) -> MetadataDTO: ...
    def change_metadata_of_chunk(
        self, id_of_chunk: str, new_metadata: MetadataDTO
    ) -> None: ...
