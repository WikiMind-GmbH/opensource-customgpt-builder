from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from src.contexts.knowledge.application.orchestration_use_cases.deletion.delete_documents import (
    DELETION_JOB_LEASE_DURATION,
    delete_claimed_document_from_all_storage_systems_and_complete_job,
)
from src.contexts.knowledge.application.ports.file_storage_port import RawFileStorePort
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)
from src.contexts.shared.typing_aliases import Factory
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(
    context=LoggerContext.KNOWLEDGE, component="process_document_deletion_jobs"
)

MAX_DELETION_RETRY_DELAY = timedelta(hours=1)


@dataclass(frozen=True)
class ClaimAndRunDocumentDeletionJobsResult:
    attempted: int
    completed: int
    failed: int


def claim_and_run_available_document_deletion_jobs(
    *,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
    limit: int = 100,
) -> ClaimAndRunDocumentDeletionJobsResult:
    """Claim and run due deletion jobs for a worker polling iteration."""
    attempted = 0
    completed = 0
    for _ in range(limit):
        now = datetime.now(UTC)
        with knowledge_uow_factory() as uow:
            job = uow.background_work.document_deletion_jobs.claim_next_available_job_and_assign_lease(
                now=now,
                lease_duration=DELETION_JOB_LEASE_DURATION,
            )
            uow.commit()
        if job is None:
            break

        attempted += 1
        try:
            delete_claimed_document_from_all_storage_systems_and_complete_job(
                job=job,
                knowledge_uow_factory=knowledge_uow_factory,
                file_storage_adapter=file_storage_adapter,
                vector_store_adapter=vector_store_adapter,
            )
            completed += 1
        except Exception as exc:
            logger.exception(
                "Garbage collection could not clean knowledge document %s",
                job.file_id,
            )
            failed_at = datetime.now(UTC)
            retry_delay = min(
                timedelta(seconds=10 * 2 ** (job.attempt_number - 1)),
                MAX_DELETION_RETRY_DELAY,
            )
            with knowledge_uow_factory() as uow:
                uow.background_work.document_deletion_jobs.release_lease_and_schedule_retry(
                    job,
                    now=failed_at,
                    next_attempt_at=failed_at + retry_delay,
                    failure_category=type(exc).__name__,
                )
                uow.commit()

    return ClaimAndRunDocumentDeletionJobsResult(
        attempted=attempted,
        completed=completed,
        failed=attempted - completed,
    )
