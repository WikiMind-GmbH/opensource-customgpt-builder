from datetime import UTC, datetime
from uuid import UUID

from src.contexts.knowledge.application.orchestration_use_cases.upload.process_document_processing_jobs import (
    claim_and_run_document_processing_job_for_file_if_available,
)
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    ExtractTextFromDocumentPort,
)
from src.contexts.knowledge.application.ports.file_storage_port import RawFileStorePort
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.task_scheduler_port import (
    TaskSchedulerPort,
)
from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.domain.models import UploadedTextLikeFile
from src.contexts.shared.typing_aliases import Factory


def upload_document_complete_workflow_return_file_id(
    file_bytes_content: bytes,
    file_name_with_ending: str,
    extract_text_from_document_adapter: ExtractTextFromDocumentPort,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    accessible_to_cgpts: list[str],
    cgpt_permissions_adapter: CgptPermissionCheckerPort,
    file_storage_adapter: RawFileStorePort,
    task_scheduler: TaskSchedulerPort,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
) -> UUID:
    cgpt_permissions_adapter.assure_user_has_access_to_cgpts(accessible_to_cgpts)
    file_type, file_name_with_ending = (
        UploadedTextLikeFile.get_text_file_type_enum_from_filename_throw_error_if_not_supported(
            filename=file_name_with_ending
        )
    )
    hash: str = UploadedTextLikeFile.calculate_hash_based_on_text_like_file_type(
        txt_like_file_type=file_type, content=file_bytes_content
    )
    with knowledge_uow_factory() as uow:
        uploaded_file = uow.knowledge_repo.get_non_deletion_pending_file_by_hash_and_lock_it_if_it_exists(
            hash_of_file=hash
        )
        file_already_exists = uploaded_file is not None
        if file_already_exists:
            file_id = uploaded_file.id
            uow.knowledge_repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
                cgpt_ids=accessible_to_cgpts, hash_of_file=hash
            )
            needs_processing = not uploaded_file.document_is_completely_processed_and_marked_as_available_in_vector_db
            if needs_processing:
                uow.background_work.document_processing_jobs.create_pending_job_if_none_exists(
                    file_id,
                    now=datetime.now(UTC),
                )
        else:
            uploaded_file = uow.knowledge_repo.create_new_file_if_hash_doesnt_exist_yet(
                filename=file_name_with_ending,
                hash=hash,
                file_type=file_type,
            )
            uow.knowledge_repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
                cgpt_ids=accessible_to_cgpts, hash_of_file=hash
            )
            file_storage_adapter.add_file(
                file_contents=file_bytes_content, file_id=uploaded_file.id
            )
            uploaded_file.mark_raw_file_was_stored()
            uow.background_work.document_processing_jobs.create_pending_job_if_none_exists(
                uploaded_file.id,
                now=datetime.now(UTC),
            )
            needs_processing = True
        uow.commit()

    if needs_processing:
        task_scheduler.add_task(
            claim_and_run_document_processing_job_for_file_if_available,
            uploaded_file.id,
            knowledge_uow_factory,
            extract_text_from_document_adapter,
            file_storage_adapter,
            vector_store_adapter,
            embedding_generator_adapter,
        )
    return uploaded_file.id
