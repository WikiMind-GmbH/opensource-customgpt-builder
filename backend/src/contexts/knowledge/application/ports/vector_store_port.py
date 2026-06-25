from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class NotFoundError(RuntimeError):
    "This object does not exist"


class InvalidEmbeddingDimension(RuntimeError):
    "The embedding dimension of passed vectors must match the one of the vevctorstore"


class NoSnippetsForPassedFileIdsExistError(RuntimeError):
    "There are no snippets from the given file ids"


class FileIdsToIncludeMustNotBeEmptyError(RuntimeError):
    "Can not query database meaningful for files that do not exist"


class ParentOrChildDTO(StrEnum):
    parent = "parent"
    child = "child"


@dataclass
class MetadataDTO:
    parent_or_child_chunk: ParentOrChildDTO
    id_of_corresponding_file: UUID
    text_content: str


@dataclass
class ChunkEmbeddingAndMetadataDTO:
    embedding_vector: list[float]
    metadata: MetadataDTO
    id_of_chunk: UUID


@dataclass
class TextChunkReturnDTO:
    id_of_chunk: UUID
    score: float


class VectorStorePortTextChunks(Protocol):
    @property
    def embedding_dimension(self) -> int:
        """Dimension expected of the vector store in its collections"""
        ...

    @property
    def collection_name(self) -> str: ...

    def return_relevant_text_snippets_ids_and_text(
        self,
        embedding_to_match: list[float],
        file_ids_to_include_in_filter: list[UUID],
        max_snippets: int = 5,
        include_only_parent_or_child_chunks: ParentOrChildDTO | None = None,
    ) -> list[TextChunkReturnDTO]: ...

    """
    Raises FileIdsToIncludeMustNotBeEmptyError and NoSnippetsForPassedFileIdsExistError
    """

    def add_chunks_with_corresponding_embeddings_and_metadata(
        self, chunk_embeddings_and_metadata_dtos: list[ChunkEmbeddingAndMetadataDTO]
    ) -> None: ...

    def return_first_thousand_embeddings_of_file_id(
        self,
        file_id: UUID,
    ) -> list[ChunkEmbeddingAndMetadataDTO]: ...

    # def get_metadata_of_chunk(self, id_of_chunk: UUID) -> MetadataDTO: ...
    # def change_metadata_of_chunk(
    #     self, id_of_chunk: str, new_metadata: MetadataDTO
    # ) -> None: ...
