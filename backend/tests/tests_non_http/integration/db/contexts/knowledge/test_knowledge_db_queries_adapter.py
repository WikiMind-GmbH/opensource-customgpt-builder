from uuid import uuid4

import pytest
from sqlalchemy import insert
from sqlalchemy.orm import Session, sessionmaker

from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    DocumentStatusDTO,
    NotFoundError,
)
from src.contexts.knowledge.domain.models import (
    TextFileTypeEnum,
    UploadedTextLikeFileProcessingStatus,
)
from src.contexts.knowledge.infrastructure.adapters.knowledge_db_queries_adapter import (
    KnowledgeDBQueriesSQAlchemyAdapter,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    cgpt_permissions_to_files,
    uploaded_text_like_file,
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
def test_returns_mapped_status_for_document_associated_with_cgpt(
    session_factory: sessionmaker[Session],
    domain_status: UploadedTextLikeFileProcessingStatus,
    expected_dto: DocumentStatusDTO,
) -> None:
    document_id = uuid4()
    cgpt_id = "accessible-cgpt"
    with session_factory() as session:
        session.execute(
            insert(uploaded_text_like_file).values(
                _id=document_id,
                _name="knowledge.txt",
                _file_type=TextFileTypeEnum.txt,
                _transformed_text=None,
                _hash_of_raw_file=str(document_id),
                _status=domain_status,
            )
        )
        session.execute(
            insert(cgpt_permissions_to_files).values(
                _id=str(uuid4()),
                file_id=document_id,
                cgpt_id=cgpt_id,
            )
        )
        session.commit()

    adapter = KnowledgeDBQueriesSQAlchemyAdapter(session_factory)

    assert adapter.check_status_of_document(document_id, cgpt_id) == expected_dto


@pytest.mark.parametrize("document_exists", (False, True))
def test_raises_same_not_found_error_for_missing_or_unassociated_document(
    session_factory: sessionmaker[Session], document_exists: bool
) -> None:
    document_id = uuid4()
    if document_exists:
        with session_factory() as session:
            session.execute(
                insert(uploaded_text_like_file).values(
                    _id=document_id,
                    _name="private.txt",
                    _file_type=TextFileTypeEnum.txt,
                    _transformed_text=None,
                    _hash_of_raw_file=str(document_id),
                    _status=UploadedTextLikeFileProcessingStatus.created,
                )
            )
            session.commit()

    adapter = KnowledgeDBQueriesSQAlchemyAdapter(session_factory)

    with pytest.raises(NotFoundError):
        adapter.check_status_of_document(document_id, "unassociated-cgpt")
