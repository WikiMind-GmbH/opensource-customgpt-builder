from src.contexts.knowledge.application.ports.vector_store_port import (
    ChunkEmbeddingAndMetadataDTO,
    MetadataDTO,
    ParentOrChildDTO,
    TextChunkReturnDTO,
)
from src.contexts.knowledge.infrastructure.adapters.vector_store_adapter import (
    QdrantVectorStoreTextChunksAdapter,
)

# class VectorStorePortTextChunks(Protocol):
#     @property
#     def embedding_dimension(self) -> int:
#         """Dimension expected of the vector store in its collections"""
#         ...

#     def return_relevant_text_snippets_ids_and_text(
#         self,
#         embedding_to_match: list[float],
#         file_ids_to_include_in_filter: list[str],
#         max_snippets: int = 5,
#         include_only_parent_or_child_chunks: ParentOrChildDTO | None = None,
#     ) -> list[TextChunkReturnDTO]: ...

#     def add_chunks_with_corresponding_embeddings_and_metadata(
#         self, chunk_embeddings_and_metadata_dtos: list[ChunkEmbeddingAndMetadataDTO]
#     ) -> None: ...


def test_simple_happy_path_add_and_return(
    fresh_qdrant_vector_store_adapter: QdrantVectorStoreTextChunksAdapter,
) -> None:
    file_id = "file-1"

    chunks_to_add = [
        ChunkEmbeddingAndMetadataDTO(
            id_of_chunk="chunk-1",
            embedding_vector=[1.0, 0.0],
            metadata=MetadataDTO(
                parent_or_child_chunk=ParentOrChildDTO.child,
                id_of_corresponding_file=file_id,
                text_content="This is the expected relevant chunk text.",
            ),
        ),
        ChunkEmbeddingAndMetadataDTO(
            id_of_chunk="chunk-2",
            embedding_vector=[0.0, 1.0],
            metadata=MetadataDTO(
                parent_or_child_chunk=ParentOrChildDTO.child,
                id_of_corresponding_file=file_id,
                text_content="This is unrelated chunk text.",
            ),
        ),
        ChunkEmbeddingAndMetadataDTO(
            id_of_chunk="chunk-3",
            embedding_vector=[-1.0, 0.0],
            metadata=MetadataDTO(
                parent_or_child_chunk=ParentOrChildDTO.child,
                id_of_corresponding_file=file_id,
                text_content="This is another unrelated chunk text.",
            ),
        ),
    ]

    fresh_qdrant_vector_store_adapter.add_chunks_with_corresponding_embeddings_and_metadata(
        chunk_embeddings_and_metadata_dtos=chunks_to_add,
    )

    returned_chunks = (
        fresh_qdrant_vector_store_adapter.return_relevant_text_snippets_ids_and_text(
            embedding_to_match=[1.0, 0.0],
            file_ids_to_include_in_filter=[file_id],
            max_snippets=1,
        )
    )

    assert returned_chunks == [
        TextChunkReturnDTO(
            id_of_chunk="chunk-1",
            metadata=MetadataDTO(
                parent_or_child_chunk=ParentOrChildDTO.child,
                id_of_corresponding_file=file_id,
                text_content="This is the expected relevant chunk text.",
            ),
        )
    ]
