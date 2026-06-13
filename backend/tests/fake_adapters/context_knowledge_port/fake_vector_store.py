from uuid import UUID

from src.contexts.knowledge.application.ports.vector_store_port import (
    ChunkEmbeddingAndMetadataDTO,
    InvalidEmbeddingDimension,
    ParentOrChildDTO,
    TextChunkReturnDTO,
    VectorStorePortTextChunks,
)


class FakeVectorStoreTextChunksAdapter(VectorStorePortTextChunks):
    def __init__(self, embedding_dimension: int) -> None:
        if embedding_dimension <= 0:
            raise InvalidEmbeddingDimension(
                f"Embedding dimension must be positive, got {embedding_dimension}."
            )

        self._embedding_dimension = embedding_dimension
        self._chunks: dict[UUID, ChunkEmbeddingAndMetadataDTO] = {}

    @property
    def collection_name(self) -> str:
        return "fake_collection"

    @property
    def embedding_dimension(self) -> int:
        return self._embedding_dimension

    def return_relevant_text_snippets_ids_and_text(
        self,
        embedding_to_match: list[float],
        file_ids_to_include_in_filter: list[UUID],
        max_snippets: int = 5,
        include_only_parent_or_child_chunks: ParentOrChildDTO | None = None,
    ) -> list[TextChunkReturnDTO]:
        if len(embedding_to_match) != self._embedding_dimension:
            raise InvalidEmbeddingDimension(
                f"Expected embedding dimension {self._embedding_dimension}, "
                f"got {len(embedding_to_match)}."
            )

        matching_chunks = [
            dto
            for dto in self._chunks.values()
            if dto.metadata.id_of_corresponding_file in file_ids_to_include_in_filter
            and (
                include_only_parent_or_child_chunks is None
                or dto.metadata.parent_or_child_chunk
                == include_only_parent_or_child_chunks
            )
        ]

        return [
            TextChunkReturnDTO(
                id_of_chunk=dto.id_of_chunk,
                score=1.0,
            )
            for dto in matching_chunks[:max_snippets]
        ]

    def add_chunks_with_corresponding_embeddings_and_metadata(
        self,
        chunk_embeddings_and_metadata_dtos: list[ChunkEmbeddingAndMetadataDTO],
    ) -> None:
        for dto in chunk_embeddings_and_metadata_dtos:
            if len(dto.embedding_vector) != self._embedding_dimension:
                raise InvalidEmbeddingDimension(
                    f"Expected embedding dimension {self._embedding_dimension}, "
                    f"got {len(dto.embedding_vector)}."
                )

            self._chunks[dto.id_of_chunk] = dto

    def return_first_thousand_embeddings_of_file_id(
        self,
        file_id: UUID,
    ) -> list[ChunkEmbeddingAndMetadataDTO]:
        return [
            dto
            for dto in self._chunks.values()
            if dto.metadata.id_of_corresponding_file == file_id
        ]
