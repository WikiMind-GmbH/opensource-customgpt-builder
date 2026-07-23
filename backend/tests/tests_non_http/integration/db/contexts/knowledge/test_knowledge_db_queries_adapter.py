from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import insert
from sqlalchemy.orm import Session, sessionmaker

from src.contexts.knowledge.application.ports.background_work import (
    DurableBackgroundJobState,
)
from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    DocumentOverviewDTO,
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
    document_deletion_jobs,
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
            session.execute(
                insert(cgpt_permissions_to_files).values(
                    _id=str(uuid4()),
                    file_id=document_id,
                    cgpt_id="different-cgpt",
                )
            )
            session.commit()

    adapter = KnowledgeDBQueriesSQAlchemyAdapter(session_factory)

    with pytest.raises(NotFoundError):
        adapter.check_status_of_document(document_id, "unassociated-cgpt")
    non_existent_document = uuid4()
    with pytest.raises(NotFoundError):
        adapter.check_status_of_document(non_existent_document, "any-cgpt")


def test_get_documents_for_cgpt_returns_only_associated_documents(
    session_factory: sessionmaker[Session],
) -> None:
    cgpt_id = "target-cgpt"
    other_cgpt_id = "other-cgpt"
    target_document_id = uuid4()
    other_document_id = uuid4()

    with session_factory() as session:
        for document_id, name in (
            (target_document_id, "target.txt"),
            (other_document_id, "other.txt"),
        ):
            session.execute(
                insert(uploaded_text_like_file).values(
                    _id=document_id,
                    _name=name,
                    _file_type=TextFileTypeEnum.txt,
                    _transformed_text=None,
                    _hash_of_raw_file=str(document_id),
                    _status=UploadedTextLikeFileProcessingStatus.raw_file_stored,
                )
            )
        session.execute(
            insert(cgpt_permissions_to_files),
            (
                {
                    "_id": str(uuid4()),
                    "file_id": target_document_id,
                    "cgpt_id": cgpt_id,
                },
                {
                    "_id": str(uuid4()),
                    "file_id": other_document_id,
                    "cgpt_id": other_cgpt_id,
                },
            ),
        )
        session.commit()

    adapter = KnowledgeDBQueriesSQAlchemyAdapter(session_factory)

    assert adapter.get_documents_for_cgpt(cgpt_id) == [
        DocumentOverviewDTO(
            document_id=target_document_id,
            name="target.txt",
            file_type=".txt",
            status=DocumentStatusDTO.raw_document_was_stored,
        )
    ]


def test_get_documents_for_cgpt_returns_empty_list_when_none_are_associated(
    session_factory: sessionmaker[Session],
) -> None:
    adapter = KnowledgeDBQueriesSQAlchemyAdapter(session_factory)

    assert adapter.get_documents_for_cgpt("cgpt-without-documents") == []


def test_get_file_associations_groups_cgpts_and_excludes_pending_deletions(
    session_factory: sessionmaker[Session],
) -> None:
    shared_file_id = uuid4()
    pending_file_id = uuid4()
    with session_factory() as session:
        for document_id in (
            shared_file_id,
            pending_file_id,
        ):
            session.execute(
                insert(uploaded_text_like_file).values(
                    _id=document_id,
                    _name=f"{document_id}.txt",
                    _file_type=TextFileTypeEnum.txt,
                    _transformed_text=None,
                    _hash_of_raw_file=str(document_id),
                    _status=UploadedTextLikeFileProcessingStatus.raw_file_stored,
                )
            )
        session.execute(
            insert(cgpt_permissions_to_files),
            (
                {
                    "_id": str(uuid4()),
                    "file_id": shared_file_id,
                    "cgpt_id": "cgpt-b",
                },
                {
                    "_id": str(uuid4()),
                    "file_id": shared_file_id,
                    "cgpt_id": "cgpt-a",
                },
                {
                    "_id": str(uuid4()),
                    "file_id": pending_file_id,
                    "cgpt_id": "cgpt-pending-delete",
                },
            ),
        )
        # Keep the file associated; the synthetic job only tests query filtering.
        now = datetime.now(UTC)
        session.execute(
            insert(document_deletion_jobs).values(
                file_id=pending_file_id,
                state=DurableBackgroundJobState.pending,
                attempt_count=0,
                next_attempt_at=now,
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    adapter = KnowledgeDBQueriesSQAlchemyAdapter(session_factory)

    assert {
        association.file_id: association.cgpt_ids
        for association in adapter.get_file_cgpt_associations()
    } == {
        shared_file_id: ["cgpt-a", "cgpt-b"],
    }
