import pytest

from src.contexts.knowledge.application.mappers import KnowledgeDBQueriesMapper
from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    DocumentStatusDTO,
)
from src.contexts.knowledge.domain.models import (
    UploadedTextLikeFileProcessingStatus,
)


@pytest.mark.parametrize(
    ("domain_status", "expected_dto"),
    (
        (
            UploadedTextLikeFileProcessingStatus.created,
            DocumentStatusDTO.initialized,
        ),
        (
            UploadedTextLikeFileProcessingStatus.raw_file_stored,
            DocumentStatusDTO.raw_document_was_stored,
        ),
        (
            UploadedTextLikeFileProcessingStatus.stored_original_preprocessed_to_text,
            DocumentStatusDTO.text_extracted_but_not_chunked,
        ),
        (
            UploadedTextLikeFileProcessingStatus.stored_original_and_preprocessed_and_chunked,
            DocumentStatusDTO.chunked_but_not_embedded,
        ),
        (
            UploadedTextLikeFileProcessingStatus.stored_preprocessed_chunked_and_embeddings_stored_in_vectorstore,
            DocumentStatusDTO.chunks_embedded_and_ready,
        ),
    ),
)
def test_document_status_domain_to_dto(
    domain_status: UploadedTextLikeFileProcessingStatus,
    expected_dto: DocumentStatusDTO,
) -> None:
    assert (
        KnowledgeDBQueriesMapper.document_status_domain_to_dto(domain_status)
        == expected_dto
    )
