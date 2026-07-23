from uuid import UUID

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
    FileIdsToIncludeMustNotBeEmptyError,
    InvalidEmbeddingDimension,
    MetadataDTO,
    NoSnippetsForPassedFileIdsExistError,
    ParentOrChildDTO,
    TextChunkReturnDTO,
    VectorStorePortTextChunks,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(
    context=LoggerContext.KNOWLEDGE, component="qdrant_vector_store_adapter"
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
        self._ensure_collection_exists()
        logger.debug("Adapter created")

    def _ensure_collection_exists(self) -> None:
        if self._client.collection_exists(
            collection_name=self._collection_name,
        ):
            logger.debug(f"Collection{self._collection_name} already exists")
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=self._embedding_dimension,
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"Collection{self._collection_name} created")

    @staticmethod
    def _qdrant_point_id_to_chunk_id(point_id: ExtendedPointId) -> UUID:
        if isinstance(point_id, UUID):
            return point_id

        if isinstance(point_id, str):
            try:
                return UUID(point_id)
            except ValueError as exc:
                raise RuntimeError(
                    f"qdrant id was string that was not able to be transformed to UUID, namely`{point_id}`"
                ) from exc

        raise RuntimeError(
            f"Expected Qdrant point id to be UUID or UUID-shaped string, got {type(point_id)}."
        )

    def _metadata_dto_to_payload_dict(
        self,
        metadata_dto: MetadataDTO,
    ) -> dict[str, str]:
        return {
            "parent_or_child_chunk": metadata_dto.parent_or_child_chunk.value,
            "id_of_corresponding_file": str(metadata_dto.id_of_corresponding_file),
            "text_content": metadata_dto.text_content,
        }

    def _payload_dict_to_metadata_dto(
        self,
        payload_dict: dict[str, object],
    ) -> MetadataDTO:
        return MetadataDTO(
            parent_or_child_chunk=ParentOrChildDTO(
                str(payload_dict["parent_or_child_chunk"])
            ),
            id_of_corresponding_file=UUID(
                str(payload_dict["id_of_corresponding_file"])
            ),
            text_content=str(payload_dict["text_content"]),
        )

    def _point_to_chunk_embedding_and_metadata_dto(
        self,
        point: models.Record,
    ) -> ChunkEmbeddingAndMetadataDTO:
        def _qdrant_vector_to_embedding_vector(
            vector: models.VectorStructOutput | None,
        ) -> list[float]:
            if not isinstance(vector, list) or any(
                isinstance(item, list) for item in vector
            ):
                raise RuntimeError("Expected Qdrant vector to be a flat list.")

            return vector  # pyright: ignore[reportReturnType] - Runtime check above rejects None, named vectors, and multivectors. Pyright cannot narrow Qdrant's VectorStructOutput to list[float] through the any(...) container check.

        if point.payload is None:
            raise RuntimeError(
                f"Qdrant point {point.id} has no payload, but metadata is required."
            )

        if point.vector is None:
            raise RuntimeError(
                f"Qdrant point {point.id} has no vector, but embedding is required."
            )

        return ChunkEmbeddingAndMetadataDTO(
            id_of_chunk=self._qdrant_point_id_to_chunk_id(point.id),
            embedding_vector=_qdrant_vector_to_embedding_vector(point.vector),
            metadata=self._payload_dict_to_metadata_dto(point.payload),
        )

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
        file_ids_of_chunks = [
            dto.metadata.id_of_corresponding_file
            for dto in chunk_embeddings_and_metadata_dtos
        ]
        logger.info(
            f"{len(chunk_embeddings_and_metadata_dtos)} Chunks of files {set(file_ids_of_chunks)} added to vectorstore: {update_result}"
        )

    def delete_embeddings_of_file(self, file_id: UUID) -> None:
        file_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="id_of_corresponding_file",
                    match=models.MatchValue(value=str(file_id)),
                )
            ]
        )
        update_result = self._client.delete(
            collection_name=self._collection_name,
            points_selector=models.FilterSelector(filter=file_filter),
            wait=True,
        )
        logger.info(
            "Deleted vector-store chunks for file %s: %s", file_id, update_result
        )

    def return_relevant_text_snippets_ids_and_text(
        self,
        embedding_to_match: list[float],
        file_ids_to_include_in_filter: list[UUID],
        max_snippets: int = 5,
        include_only_parent_or_child_chunks: ParentOrChildDTO | None = None,
    ) -> list[TextChunkReturnDTO]:
        if len(embedding_to_match) != self.embedding_dimension:
            raise InvalidEmbeddingDimension(
                f"expected embedding dim {self.embedding_dimension}, got {len(embedding_to_match)}"
            )
        if file_ids_to_include_in_filter == []:
            raise FileIdsToIncludeMustNotBeEmptyError
        # class MetadataDTO:
        #     parent_or_child_chunk: ParentOrChildDTO
        #     id_of_corresponding_file: str
        #     text_content: str
        filter = []
        filter_for_chunks_with_file_id = models.FieldCondition(
            key="id_of_corresponding_file",
            match=models.MatchAny(
                any=[str(file_id) for file_id in file_ids_to_include_in_filter]
            ),
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
        if response_points == []:
            raise NoSnippetsForPassedFileIdsExistError
        text_chunk_return_dtos = [
            TextChunkReturnDTO(
                id_of_chunk=self._qdrant_point_id_to_chunk_id(point.id),
                score=point.score,
            )
            for point in response_points
        ]
        logger.info(f"Returned {len(text_chunk_return_dtos)} text chunk ids")
        return text_chunk_return_dtos

    def get_metadata_of_chunk(self, id_of_chunk: str) -> MetadataDTO:
        raise NotImplementedError

    def change_metadata_of_chunk(
        self, id_of_chunk: str, new_metadata: MetadataDTO
    ) -> None:
        return None

    def return_first_thousand_embeddings_of_file_id(
        self,
        file_id: UUID,
    ) -> list[ChunkEmbeddingAndMetadataDTO]:
        file_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="id_of_corresponding_file",
                    match=models.MatchValue(value=str(file_id)),
                )
            ]
        )

        points, _next_page_offset = self._client.scroll(
            collection_name=self._collection_name,
            scroll_filter=file_filter,
            limit=1000,
            with_payload=True,
            with_vectors=True,
        )

        return [
            self._point_to_chunk_embedding_and_metadata_dto(point) for point in points
        ]
