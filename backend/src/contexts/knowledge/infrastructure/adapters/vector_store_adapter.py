from qdrant_client import QdrantClient, models
from qdrant_client.models import (
    Distance,
    ExtendedPointId,
    PointStruct,
    UpdateResult,
    VectorParams,
)

from src.contexts.knowledge.application.ports.vector_store_port import (
    ChunkEmbeddingAndMetadataDTO,
    InvalidEmbeddingDimension,
    MetadataDTO,
    ParentOrChildDTO,
    TextChunkReturnDTO,
    VectorStorePortTextChunks,
)


class QdrantVectorStoreTextChunksAdapter(VectorStorePortTextChunks):
    def __init__(
        self,
        db_url: str,
        embedding_dimension: int,
        create_adapter_for_testing_with_test_collection: bool = False,
    ) -> None:
        self._embedding_dimension = embedding_dimension
        self._collection_name = (
            "TextChunksCollection"
            if not create_adapter_for_testing_with_test_collection
            else "TestTextChunksCollection"
        )
        self._client = QdrantClient(url=db_url)
        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=self._embedding_dimension, distance=Distance.COSINE
            ),
        )

    def _metadata_dto_to_payload_dict(self, metadata_dto: MetadataDTO):
        metadata_dict = {
            "parent_or_child_chunk": str(metadata_dto.parent_or_child_chunk),
            "id_of_corresponding_file": metadata_dto.id_of_corresponding_file,
            "text_content": metadata_dto.text_content,
        }
        return metadata_dict

    def close_client(self):
        self._client.close()

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def is_a_testing_collection(self):
        return self._collection_name == "TestTextChunksCollection"

    @property
    def embedding_dimension(self) -> int:
        """Dimension expected of the vector store in its collections"""
        return self._embedding_dimension

    def add_chunks_with_corresponding_embeddings_and_metadata(
        self, chunk_embeddings_and_metadata_dtos: list[ChunkEmbeddingAndMetadataDTO]
    ) -> None:
        for chunk_embedding_and_metadata_dto in chunk_embeddings_and_metadata_dtos:
            embedding_dim_of_chunk = len(
                chunk_embedding_and_metadata_dto.embedding_vector
            )
            if embedding_dim_of_chunk != self.embedding_dimension:
                raise InvalidEmbeddingDimension(
                    f"expected embedding dim {self.embedding_dimension}, got {embedding_dim_of_chunk}"
                )
        update_result: UpdateResult = self._client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(
                    id=chunk_embedding_and_metadata_dto.id_of_chunk,
                    vector=chunk_embedding_and_metadata_dto.embedding_vector,
                    payload=self._metadata_dto_to_payload_dict(
                        chunk_embedding_and_metadata_dto.metadata
                    ),
                )
                for chunk_embedding_and_metadata_dto in chunk_embeddings_and_metadata_dtos
            ],
        )
        print(update_result)  # PLACEHOLDRE FOR LOGGING LATER

    def return_relevant_text_snippets_ids_and_text(
        self,
        embedding_to_match: list[float],
        file_ids_to_include_in_filter: list[str],
        max_snippets: int = 5,
        include_only_parent_or_child_chunks: ParentOrChildDTO | None = None,
    ) -> list[TextChunkReturnDTO]:
        @staticmethod
        def _qdrant_point_id_to_chunk_id(point_id: ExtendedPointId) -> str:
            if not isinstance(point_id, str):
                raise RuntimeError(
                    f"Expected Qdrant point id to be str, got {type(point_id)}."
                )
            return point_id

        if len(embedding_to_match) != self.embedding_dimension:
            raise InvalidEmbeddingDimension(
                f"expected embedding dim {self.embedding_dimension}, got {len(embedding_to_match)}"
            )

        # class MetadataDTO:
        #     parent_or_child_chunk: ParentOrChildDTO
        #     id_of_corresponding_file: str
        #     text_content: str
        filter = []
        filter_for_chunks_with_file_id = models.FieldCondition(
            key="id_of_corresponding_file",
            match=models.MatchAny(any=file_ids_to_include_in_filter),
        )
        filter.append(filter_for_chunks_with_file_id)

        filter_for_parent_or_child = models.FieldCondition(
            key="parent_or_child_chunk",
            match=models.MatchText(text=str(include_only_parent_or_child_chunks)),
        )
        if include_only_parent_or_child_chunks is not None:
            filter.append(filter_for_parent_or_child)

        query_filter = models.Filter(must=filter)

        response = self._client.query_points(
            collection_name=self._collection_name,
            query=embedding_to_match,
            query_filter=query_filter,
            limit=max_snippets,
            with_payload=True,
        )
        response_points = response.points

        text_chunk_return_dtos = [
            TextChunkReturnDTO(
                id_of_chunk=_qdrant_point_id_to_chunk_id(point.id), score=point.score
            )
            for point in response_points
        ]
        return text_chunk_return_dtos

    def get_metadata_of_chunk(self, id_of_chunk: str) -> MetadataDTO:
        return None

    def change_metadata_of_chunk(
        self, id_of_chunk: str, new_metadata: MetadataDTO
    ) -> None:
        return None
