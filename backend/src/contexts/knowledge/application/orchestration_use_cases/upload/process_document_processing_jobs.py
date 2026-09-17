from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.contexts.knowledge.application.mappers import (
    MappersVectorStore,
    PreProcessTextLikesPortMapper,
)
from src.contexts.knowledge.application.ports.background_work import (
    BackgroundJobLeaseIsNoLongerOwnedError,
    DocumentProcessingJobLease,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    ExtractTextFromDocumentPort,
)
from src.contexts.knowledge.application.ports.file_storage_port import RawFileStorePort
from src.contexts.knowledge.application.ports.knowledge_repo import (
    FileDoesNotExistError,
)
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.vector_store_port import (
    ChunkEmbeddingAndMetadataDTO,
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.domain.models import (
    NextNecessaryProcessingStep,
    TextFileChunk,
    UploadedTextLikeFileProcessingStatus,
)
from src.contexts.shared.typing_aliases import Factory
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(
    context=LoggerContext.KNOWLEDGE, component="process_document_processing_jobs"
)

PROCESSING_JOB_LEASE_DURATION = timedelta(minutes=30)
MAX_PROCESSING_ATTEMPTS = 5
MAX_PROCESSING_RETRY_DELAY = timedelta(hours=1)


def claim_and_run_document_processing_job_for_file_if_available(
    uploaded_file_id: UUID,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    extract_text_from_document_adapter: ExtractTextFromDocumentPort,
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
) -> bool:
    now = datetime.now(UTC)
    with knowledge_uow_factory() as uow:
        job = uow.background_work.document_processing_jobs.claim_job_for_file_if_available_and_assign_lease(
            uploaded_file_id,
            now=now,
            lease_duration=PROCESSING_JOB_LEASE_DURATION,
        )
        uow.commit()
    if job is None:
        return False

    return _run_claimed_document_processing_job(
        job=job,
        knowledge_uow_factory=knowledge_uow_factory,
        extract_text_from_document_adapter=extract_text_from_document_adapter,
        file_storage_adapter=file_storage_adapter,
        vector_store_adapter=vector_store_adapter,
        embedding_generator_adapter=embedding_generator_adapter,
    )


def claim_and_run_next_available_document_processing_job(
    knowledge_uow_factory: Factory[KnowledgeUOW],
    extract_text_from_document_adapter: ExtractTextFromDocumentPort,
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
) -> bool:
    now = datetime.now(UTC)
    with knowledge_uow_factory() as uow:
        job = uow.background_work.document_processing_jobs.claim_next_available_job_and_assign_lease(
            now=now,
            lease_duration=PROCESSING_JOB_LEASE_DURATION,
        )
        uow.commit()
    if job is None:
        return False

    return _run_claimed_document_processing_job(
        job=job,
        knowledge_uow_factory=knowledge_uow_factory,
        extract_text_from_document_adapter=extract_text_from_document_adapter,
        file_storage_adapter=file_storage_adapter,
        vector_store_adapter=vector_store_adapter,
        embedding_generator_adapter=embedding_generator_adapter,
    )


def _run_claimed_document_processing_job(
    *,
    job: DocumentProcessingJobLease,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    extract_text_from_document_adapter: ExtractTextFromDocumentPort,
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
) -> bool:
    try:
        resume_document_processing_from_persisted_state(
            uploaded_file_id=job.file_id,
            knowledge_uow_factory=knowledge_uow_factory,
            extract_text_from_document_adapter=extract_text_from_document_adapter,
            file_storage_adapter=file_storage_adapter,
            vector_store_adapter=vector_store_adapter,
            embedding_generator_adapter=embedding_generator_adapter,
        )
        with knowledge_uow_factory() as uow:
            uow.background_work.document_processing_jobs.delete_job_after_successful_completion_if_lease_is_still_owned(
                job
            )
            uow.commit()
        logger.info("Completed processing knowledge document %s", job.file_id)
        return True
    except BackgroundJobLeaseIsNoLongerOwnedError:
        logger.info(
            "Stopped processing knowledge document %s because its job was cancelled",
            job.file_id,
        )
        return False
    except Exception as exc:
        logger.exception(
            "Processing knowledge document %s failed on attempt %s",
            job.file_id,
            job.attempt_number,
        )
        failed_at = datetime.now(UTC)
        try:
            with knowledge_uow_factory() as uow:
                if job.attempt_number >= MAX_PROCESSING_ATTEMPTS:
                    uow.background_work.document_processing_jobs.release_lease_and_mark_job_as_permanently_failed(
                        job,
                        now=failed_at,
                        failure_category=type(exc).__name__,
                    )
                else:
                    retry_delay = min(
                        timedelta(seconds=10 * 2 ** (job.attempt_number - 1)),
                        MAX_PROCESSING_RETRY_DELAY,
                    )
                    uow.background_work.document_processing_jobs.release_lease_and_schedule_retry(
                        job,
                        now=failed_at,
                        next_attempt_at=failed_at + retry_delay,
                        failure_category=type(exc).__name__,
                    )
                uow.commit()
        except BackgroundJobLeaseIsNoLongerOwnedError:
            logger.info(
                "Did not retry processing document %s because its job was cancelled",
                job.file_id,
            )
        return False


def resume_document_processing_from_persisted_state(
    uploaded_file_id: UUID,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    extract_text_from_document_adapter: ExtractTextFromDocumentPort,
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
):
    with knowledge_uow_factory() as uow:
        uploaded_file = uow.knowledge_repo.get_file(uploaded_file_id)
        if uploaded_file.status == UploadedTextLikeFileProcessingStatus.deletion_pending:
            return
        if uploaded_file.document_is_completely_processed_and_marked_as_available_in_vector_db:
            return
        uploaded_file.assert_document_is_in_processing_phase()
        next_necessary_processing_step = (
            uploaded_file.next_necessary_processing_step_if_in_processing_phase()
        )
    if next_necessary_processing_step == NextNecessaryProcessingStep.extract_text:
        extract_text_from_document(
            uploaded_file_id=uploaded_file_id,
            knowledge_uow_factory=knowledge_uow_factory,
            extract_text_from_document_adapter=extract_text_from_document_adapter,
            file_storage_adapter=file_storage_adapter,
        )
        chunk_uploaded_file(
            uploaded_file_id=uploaded_file_id,
            knowledge_uow_factory=knowledge_uow_factory,
        )
        create_and_store_embeddings_for_all_document_chunks(
            uploaded_file_id=uploaded_file_id,
            knowledge_uow_factory=knowledge_uow_factory,
            vector_store_adapter=vector_store_adapter,
            embedding_generator_adapter=embedding_generator_adapter,
        )
    if next_necessary_processing_step == NextNecessaryProcessingStep.chunking:
        chunk_uploaded_file(
            uploaded_file_id=uploaded_file_id,
            knowledge_uow_factory=knowledge_uow_factory,
        )
        create_and_store_embeddings_for_all_document_chunks(
            uploaded_file_id=uploaded_file_id,
            knowledge_uow_factory=knowledge_uow_factory,
            vector_store_adapter=vector_store_adapter,
            embedding_generator_adapter=embedding_generator_adapter,
        )
    if next_necessary_processing_step == NextNecessaryProcessingStep.create_and_store_embeddings:
        create_and_store_embeddings_for_all_document_chunks(
            uploaded_file_id=uploaded_file_id,
            knowledge_uow_factory=knowledge_uow_factory,
            vector_store_adapter=vector_store_adapter,
            embedding_generator_adapter=embedding_generator_adapter,
        )


def extract_text_from_document(
    uploaded_file_id: UUID,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    extract_text_from_document_adapter: ExtractTextFromDocumentPort,
    file_storage_adapter: RawFileStorePort,
):
    with knowledge_uow_factory() as uow:
        uploaded_file = uow.knowledge_repo.get_file(uploaded_file_id)

    file_contents: bytes = file_storage_adapter.get_file(file_id=uploaded_file_id)
    file_content_processed_to_string: str = extract_text_from_document_adapter.process_document_to_string_based_on_file_type(
        file_type=PreProcessTextLikesPortMapper.domain_to_adapter_file_types(
            uploaded_file.file_type
        ),
        raw_file_content=file_contents,
    )
    with knowledge_uow_factory() as uow:
        uploaded_file = uow.knowledge_repo.get_file(uploaded_file_id)
        uploaded_file.set_transformed_text(text=file_content_processed_to_string)
        uow.commit()


def chunk_uploaded_file(
    uploaded_file_id: UUID,
    knowledge_uow_factory: Factory[KnowledgeUOW],
) -> None:
    with knowledge_uow_factory() as uow:
        uploaded_file = uow.knowledge_repo.get_file(uploaded_file_id)

    chunks_of_document: list[TextFileChunk] = uploaded_file.create_chunks_without_assigning_them_to_document_include_chunking_strategy()

    with knowledge_uow_factory() as setter_uow:
        uploaded_file = setter_uow.knowledge_repo.get_file(uploaded_file.id)
        uploaded_file.assign_chunks_created_with_domain_method_to_document(
            chunks_of_document
        )
        setter_uow.commit()


def create_and_store_embeddings_for_all_document_chunks(
    knowledge_uow_factory: Factory[KnowledgeUOW],
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
    uploaded_file_id: UUID,
):
    with knowledge_uow_factory() as uow:
        chunks = uow.knowledge_repo.get_chunks_of_document(file_id=uploaded_file_id)
    chunks_texts: list[str] = [chunk.text_content for chunk in chunks]
    chunks_embeddings: list[list[float]] = (
        embedding_generator_adapter.create_embeddings_for_texts(texts=chunks_texts)
    )
    chunks_with_corresponding_embeddings: list[tuple[TextFileChunk, list[float]]] = (
        list(zip(chunks, chunks_embeddings, strict=True))
    )

    chunk_embeddings_and_metadata_dtos: list[ChunkEmbeddingAndMetadataDTO] = (
        MappersVectorStore.application_types_to_chunk_embedding_and_metadata_dtos(
            chunks_with_corresponding_embeddings=chunks_with_corresponding_embeddings
        )
    )
    with knowledge_uow_factory() as uow:
        try:
            uploaded_file = uow.knowledge_repo.get_file_and_lock_it_for_exclusive_update(
                uploaded_file_id
            )
        except FileDoesNotExistError:
            return
        if uow.background_work.document_deletion_jobs.check_if_job_exists_for_file(
            uploaded_file_id
        ):
            return
        vector_store_adapter.add_chunks_with_corresponding_embeddings_and_metadata(
            chunk_embeddings_and_metadata_dtos=chunk_embeddings_and_metadata_dtos
        )
        uploaded_file.mark_chunks_are_embedded_and_added_to_vectorstore()
        uow.commit()
