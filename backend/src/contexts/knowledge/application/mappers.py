from typing import assert_never

from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    SupportedFileTypesEnum,
)
from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    DocumentOverviewDTO,
    DocumentStatusDTO,
)
from src.contexts.knowledge.application.ports.vector_store_port import (
    ChunkEmbeddingAndMetadataDTO,
    MetadataDTO,
    ParentOrChildDTO,
)
from src.contexts.knowledge.domain.models import (
    ParentOrChild,
    TextFileChunk,
    TextFileTypeEnum,
    UploadedTextLikeFile,
    UploadedTextLikeFileProcessingStatus,
)


class KnowledgeDBQueriesMapper:
    @staticmethod
    def document_status_domain_to_dto(
        status: UploadedTextLikeFileProcessingStatus,
    ) -> DocumentStatusDTO:
        match status:
            case UploadedTextLikeFileProcessingStatus.created:
                return DocumentStatusDTO.initialized
            case UploadedTextLikeFileProcessingStatus.raw_file_stored:
                return DocumentStatusDTO.raw_document_was_stored
            case UploadedTextLikeFileProcessingStatus.stored_original_preprocessed_to_text:
                return DocumentStatusDTO.text_extracted_but_not_chunked
            case UploadedTextLikeFileProcessingStatus.stored_original_and_preprocessed_and_chunked:
                return DocumentStatusDTO.chunked_but_not_embedded
            case UploadedTextLikeFileProcessingStatus.stored_preprocessed_chunked_and_embeddings_stored_in_vectorstore:
                return DocumentStatusDTO.chunks_embedded_and_ready
            case _:
                assert_never(status)

    @classmethod
    def document_overview_domain_to_dto(
        cls, document: UploadedTextLikeFile
    ) -> DocumentOverviewDTO:
        return DocumentOverviewDTO(
            document_id=document.id,
            name=document.name,
            file_type=document.file_type.value,
            status=cls.document_status_domain_to_dto(document.status),
        )


class PreProcessTextLikesPortMapper:
    @staticmethod
    def adapter_to_domain_file_types(
        adapter_type: SupportedFileTypesEnum,
    ) -> TextFileTypeEnum:
        match adapter_type:
            case SupportedFileTypesEnum.txt:
                return TextFileTypeEnum.txt
            case _:
                assert_never(adapter_type)

    @staticmethod
    def domain_to_adapter_file_types(
        domain_type: TextFileTypeEnum,
    ) -> SupportedFileTypesEnum:
        match domain_type:
            case TextFileTypeEnum.txt:
                return SupportedFileTypesEnum.txt
            case _:
                assert_never(domain_type)


class MappersVectorStore:
    @staticmethod
    def parent_or_child_domain_to_dto(
        parent_or_child: ParentOrChild,
    ) -> ParentOrChildDTO:
        match parent_or_child:
            case ParentOrChild.parent:
                return ParentOrChildDTO.parent
            case ParentOrChild.child:
                return ParentOrChildDTO.child
            case _:
                assert_never(parent_or_child)

    @staticmethod
    def parent_or_child_dto_to_domain(
        dto: ParentOrChildDTO,
    ) -> ParentOrChild:
        match dto:
            case ParentOrChildDTO.parent:
                return ParentOrChild.parent
            case ParentOrChildDTO.child:
                return ParentOrChild.child
            case _:
                assert_never(dto)

    @staticmethod
    def text_file_chunk_domain_to_metadata_dto(
        text_file_chunk: TextFileChunk,
    ) -> MetadataDTO:
        return MetadataDTO(
            parent_or_child_chunk=MappersVectorStore.parent_or_child_domain_to_dto(
                text_file_chunk.is_parent_or_child
            ),
            id_of_corresponding_file=text_file_chunk.corresponding_text_file_id,
            text_content=text_file_chunk.text_content,
        )

    @staticmethod
    def application_types_to_chunk_embedding_and_metadata_dtos(
        chunks_with_corresponding_embeddings: list[tuple[TextFileChunk, list[float]]],
    ) -> list[ChunkEmbeddingAndMetadataDTO]:
        return [
            ChunkEmbeddingAndMetadataDTO(
                embedding_vector=embedding,
                metadata=MappersVectorStore.text_file_chunk_domain_to_metadata_dto(
                    text_file_chunk
                ),
                id_of_chunk=text_file_chunk.id,
            )
            for text_file_chunk, embedding in chunks_with_corresponding_embeddings
        ]
