from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class NotFoundError(RuntimeError):
    "This object does not exist"


class ParentOrChild(StrEnum):
    parent = "parent"
    child = "child"


@dataclass
class MetadataDTO:
    parent_or_child_chunk: ParentOrChild
    id_of_corresponding_file: str
    text_content: str


@dataclass
class AddChunkEmbeddingsDTO:
    embedding_vector: list[float]
    metadata: MetadataDTO
    id_of_chunk: str


@dataclass
class TextChunkReturnDTO:
    id_of_chunk: str
    text_snippet: str


class VectorStorePortTextChunks(Protocol):
    def return_relevant_text_snippets_ids_and_text(
        self,
        file_ids: list[str],
        max_snippets: int = 5,
    ) -> list[TextChunkReturnDTO]: ...
    def add_chunk_with_embedding(self, chunk: AddChunkEmbeddingsDTO) -> None: ...

    def get_metadata_of_chunk(self, id_of_chunk: str) -> MetadataDTO: ...
    def change_metadata_of_chunk(
        self, id_of_chunk: str, new_metadata: MetadataDTO
    ) -> None: ...
