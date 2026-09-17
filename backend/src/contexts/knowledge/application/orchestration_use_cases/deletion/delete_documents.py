from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.contexts.knowledge.application.ports.background_work import (
    DocumentDeletionJobLease,
)
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
)
from src.contexts.knowledge.application.ports.file_storage_port import (
    FileNotFoundError as RawFileNotFoundError,
)
from src.contexts.knowledge.application.ports.file_storage_port import RawFileStorePort
from src.contexts.knowledge.application.ports.knowledge_repo import (
    FileDoesNotExistError,
)
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.domain.models import UploadedTextLikeFileProcessingStatus
from src.contexts.shared.typing_aliases import Factory
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(
    context=LoggerContext.KNOWLEDGE, component="delete_documents_use_case"
)

DELETION_JOB_LEASE_DURATION = timedelta(minutes=30)


class DocumentCleanupFailedError(RuntimeError):
    "Some documents could not be removed from every storage system."


@dataclass(frozen=True)
class DocumentDeletionJobLeaseBatchResult:
    attempted: int
    completed: int
    failed: int


def delete_claimed_document_from_all_storage_systems_and_complete_job(
    *,
    job: DocumentDeletionJobLease,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
) -> None:
    """Delete one leased document and complete its deletion job."""
    with knowledge_uow_factory() as uow:
        try:
            uploaded_file = uow.knowledge_repo.get_file_and_lock_it_for_exclusive_update_and_assure_no_cgpt_associated(
                job.file_id
            )
        except FileDoesNotExistError:
            uow.background_work.document_deletion_jobs.delete_job_after_successful_completion_if_lease_is_still_owned(
                job
            )
            uow.commit()
            return

        if uploaded_file.status != UploadedTextLikeFileProcessingStatus.deletion_pending:
            uow.background_work.document_deletion_jobs.delete_job_after_successful_completion_if_lease_is_still_owned(
                job
            )
            uow.commit()
            logger.info(
                "Skipped deletion cleanup for document %s because it is no longer pending deletion",
                job.file_id,
            )
            return
        uow.commit()

    vector_store_adapter.delete_embeddings_of_file(job.file_id)
    try:
        file_storage_adapter.delete_file(job.file_id)
    except RawFileNotFoundError as exc:
        logger.warning(
            "Raw file %s was already absent while deletion was pending: %s",
            job.file_id,
            exc,
        )

    with knowledge_uow_factory() as uow:
        uow.knowledge_repo.delete_file_if_it_exists_after_locking_it_for_exclusive_update_assure_no_cgpt_associated(
            job.file_id
        )
        uow.background_work.document_deletion_jobs.delete_job_after_successful_completion_if_lease_is_still_owned(
            job
        )
        uow.commit()

    logger.info("Fully deleted knowledge document %s", job.file_id)


def delete_documents_from_cgpt(
    *,
    cgpt_id: str,
    file_ids: list[UUID],
    cgpt_permissions_adapter: CgptPermissionCheckerPort,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
) -> None:
    """Remove documents from one CustomGPT and clean newly orphaned documents."""
    cgpt_permissions_adapter.assure_user_has_access_to_cgpts([cgpt_id])

    now = datetime.now(UTC)
    with knowledge_uow_factory() as uow:
        file_ids_without_remaining_cgpt_access = uow.knowledge_repo.remove_cgpt_access_from_files_and_return_ids_of_files_without_remaining_access(
            cgpt_id=cgpt_id, file_ids=file_ids
        )
        jobs: list[DocumentDeletionJobLease] = []
        for file_id in file_ids_without_remaining_cgpt_access:
            uow.background_work.document_processing_jobs.delete_job_for_file_if_it_exists_regardless_of_lease(
                file_id
            )
            job = uow.background_work.document_deletion_jobs.create_pending_job_if_none_exists_then_claim_it_and_assign_lease(
                file_id,
                now=now,
                lease_duration=DELETION_JOB_LEASE_DURATION,
            )
            if job is not None:
                jobs.append(job)
        uow.commit()

    failures: list[tuple[UUID, Exception]] = []
    for job in jobs:
        try:
            delete_claimed_document_from_all_storage_systems_and_complete_job(
                job=job,
                knowledge_uow_factory=knowledge_uow_factory,
                file_storage_adapter=file_storage_adapter,
                vector_store_adapter=vector_store_adapter,
            )
        except Exception as exc:
            logger.exception(
                "Knowledge document %s remains pending deletion after cleanup failed",
                job.file_id,
            )
            with knowledge_uow_factory() as uow:
                uow.background_work.document_deletion_jobs.release_lease_and_make_job_immediately_available_for_retry(
                    job,
                    now=datetime.now(UTC),
                    failure_category=type(exc).__name__,
                )
                uow.commit()
            failures.append((job.file_id, exc))

    if failures:
        failed_ids = [file_id for file_id, _ in failures]
        raise DocumentCleanupFailedError(
            f"Cleanup remains pending for document ids {failed_ids}"
        ) from failures[0][1]
