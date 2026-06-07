import pytest

from src.contexts.knowledge.application.orchestration_use_cases.upload_document_use_case import (
    upload_document_complete_workflow_return_file_id,
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
from src.contexts.knowledge.domain.models import (
    DocumentIsNotInProcessingPhaseError,
    TextFileTypeEnum,
    UploadedTextLikeFile,
    UploadedTextLikeFileProcessingStatus,
)
from src.contexts.shared.typing_aliases import Factory
from tests.fake_adapters.context_knowledge_port.fake_task_scheduler import (
    FakeTaskScheduler,
)

# def upload_document_complete_workflow_return_file_id(
#     file_bytes_content: bytes,
#     file_name_with_ending: str,
#     extract_text_from_document_adapter: ExtractTextFromDocumentPort,
#     knowledge_uow_factory: Factory[KnowledgeUOW],
#     accessible_to_cgpts: list[str],
#     cgpt_permissions_adapter: CgptPermissionCheckerPort,
#     file_storage_adapter: RawFileStorePort,
#     task_scheduler: TaskSchedulerPort,
#     vector_store_adapter: VectorStorePortTextChunks,
#     embedding_generator_adapter: EmbeddingGeneratorPort,
# ) -> UUID:


class TestUploadDocumentcompleteWorkflowReturnFileId:
    @staticmethod
    def test_raises_if_user_does_not_have_permission_to_cgpt(
        extract_text_from_document_adapter: ExtractTextFromDocumentPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
        cgpt_permission_checker_false_return: CgptPermissionCheckerPort,
        file_store: RawFileStorePort,
        fake_task_scheduler: TaskSchedulerPort,
        fake_vector_store: VectorStorePortTextChunks,
        fake_embedding_generator: EmbeddingGeneratorPort,
    ):
        with pytest.raises(Exception):
            upload_document_complete_workflow_return_file_id(
                file_bytes_content=b"asd",
                file_name_with_ending="should_fail.txt",
                extract_text_from_document_adapter=extract_text_from_document_adapter,
                knowledge_uow_factory=knowledge_uow_factory,
                accessible_to_cgpts=["qas"],
                cgpt_permissions_adapter=cgpt_permission_checker_false_return,
                file_storage_adapter=file_store,
                task_scheduler=fake_task_scheduler,
                vector_store_adapter=fake_vector_store,
                embedding_generator_adapter=fake_embedding_generator,
            )

    @staticmethod
    def test_no_raises_if_user_does_have_permission_to_cgpt(
        extract_text_from_document_adapter: ExtractTextFromDocumentPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
        cgpt_permission_checker_true_return: CgptPermissionCheckerPort,
        file_store: RawFileStorePort,
        fake_task_scheduler: TaskSchedulerPort,
        fake_vector_store: VectorStorePortTextChunks,
        fake_embedding_generator: EmbeddingGeneratorPort,
    ):
        upload_document_complete_workflow_return_file_id(
            file_bytes_content=b"asd",
            file_name_with_ending="should_not_fail.txt",
            extract_text_from_document_adapter=extract_text_from_document_adapter,
            knowledge_uow_factory=knowledge_uow_factory,
            accessible_to_cgpts=["qas"],
            cgpt_permissions_adapter=cgpt_permission_checker_true_return,
            file_storage_adapter=file_store,
            task_scheduler=fake_task_scheduler,
            vector_store_adapter=fake_vector_store,
            embedding_generator_adapter=fake_embedding_generator,
        )

    @staticmethod
    def test_uploading_same_file_second_time_returns_same_id_even_with_different_file_name(
        extract_text_from_document_adapter: ExtractTextFromDocumentPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
        cgpt_permission_checker_true_return: CgptPermissionCheckerPort,
        file_store: RawFileStorePort,
        fake_task_scheduler: TaskSchedulerPort,
        fake_vector_store: VectorStorePortTextChunks,
        fake_embedding_generator: EmbeddingGeneratorPort,
    ):
        same_file_bytes_content = b"asd"
        name_one = "file.txt"
        name_two = "i-am-the-same-file.txt"

        first_file_id = upload_document_complete_workflow_return_file_id(
            file_bytes_content=same_file_bytes_content,
            file_name_with_ending=name_one,
            extract_text_from_document_adapter=extract_text_from_document_adapter,
            knowledge_uow_factory=knowledge_uow_factory,
            accessible_to_cgpts=["qas"],
            cgpt_permissions_adapter=cgpt_permission_checker_true_return,
            file_storage_adapter=file_store,
            task_scheduler=fake_task_scheduler,
            vector_store_adapter=fake_vector_store,
            embedding_generator_adapter=fake_embedding_generator,
        )
        second_file_id = upload_document_complete_workflow_return_file_id(
            file_bytes_content=same_file_bytes_content,
            file_name_with_ending=name_two,
            extract_text_from_document_adapter=extract_text_from_document_adapter,
            knowledge_uow_factory=knowledge_uow_factory,
            accessible_to_cgpts=["qas"],
            cgpt_permissions_adapter=cgpt_permission_checker_true_return,
            file_storage_adapter=file_store,
            task_scheduler=fake_task_scheduler,
            vector_store_adapter=fake_vector_store,
            embedding_generator_adapter=fake_embedding_generator,
        )

        assert first_file_id == second_file_id, (
            "Uploading a file with the same byte content (i.e. the same file) a second time should return the originals file id instead of creating a copy "
        )

    @staticmethod
    def test_uploading_different_files_returns_different_ids_even_with_same_file_name(
        extract_text_from_document_adapter: ExtractTextFromDocumentPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
        cgpt_permission_checker_true_return: CgptPermissionCheckerPort,
        file_store: RawFileStorePort,
        fake_task_scheduler: TaskSchedulerPort,
        fake_vector_store: VectorStorePortTextChunks,
        fake_embedding_generator: EmbeddingGeneratorPort,
    ):
        file_bytes_content_file_one = b"asd"
        file_bytes_content_file_two = b"qwe"
        name_one = "file.txt"

        first_file_id = upload_document_complete_workflow_return_file_id(
            file_bytes_content=file_bytes_content_file_one,
            file_name_with_ending=name_one,
            extract_text_from_document_adapter=extract_text_from_document_adapter,
            knowledge_uow_factory=knowledge_uow_factory,
            accessible_to_cgpts=["qas"],
            cgpt_permissions_adapter=cgpt_permission_checker_true_return,
            file_storage_adapter=file_store,
            task_scheduler=fake_task_scheduler,
            vector_store_adapter=fake_vector_store,
            embedding_generator_adapter=fake_embedding_generator,
        )
        second_file_id = upload_document_complete_workflow_return_file_id(
            file_bytes_content=file_bytes_content_file_two,
            file_name_with_ending=name_one,
            extract_text_from_document_adapter=extract_text_from_document_adapter,
            knowledge_uow_factory=knowledge_uow_factory,
            accessible_to_cgpts=["qas"],
            cgpt_permissions_adapter=cgpt_permission_checker_true_return,
            file_storage_adapter=file_store,
            task_scheduler=fake_task_scheduler,
            vector_store_adapter=fake_vector_store,
            embedding_generator_adapter=fake_embedding_generator,
        )

        assert not first_file_id == second_file_id, (
            "Uploading a file with the same name but with different content should return a different id"
        )

    @staticmethod
    def test_complete_workflow_return_file_id_new_file_chunks_and_embeddings_are_created_and_same_number(
        extract_text_from_document_adapter: ExtractTextFromDocumentPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
        cgpt_permission_checker_true_return: CgptPermissionCheckerPort,
        file_store: RawFileStorePort,
        fake_task_scheduler: FakeTaskScheduler,
        fake_vector_store: VectorStorePortTextChunks,
        fake_embedding_generator: EmbeddingGeneratorPort,
        fabricated_text_document_bytes: bytes,
    ):
        hash: str = UploadedTextLikeFile.calculate_hash_based_on_text_like_file_type(
            txt_like_file_type=TextFileTypeEnum.txt,
            content=fabricated_text_document_bytes,
        )
        with knowledge_uow_factory() as uow:
            file_already_exists: bool = uow.knowledge_repo.check_if_hash_already_exists(
                hash=hash
            )
        assert not file_already_exists

        first_file_id = upload_document_complete_workflow_return_file_id(
            file_bytes_content=fabricated_text_document_bytes,
            file_name_with_ending="name_one.txt",
            extract_text_from_document_adapter=extract_text_from_document_adapter,
            knowledge_uow_factory=knowledge_uow_factory,
            accessible_to_cgpts=["qas"],
            cgpt_permissions_adapter=cgpt_permission_checker_true_return,
            file_storage_adapter=file_store,
            task_scheduler=fake_task_scheduler,
            vector_store_adapter=fake_vector_store,
            embedding_generator_adapter=fake_embedding_generator,
        )
        fake_task_scheduler.run_all()

        with knowledge_uow_factory() as uow:
            file = uow.knowledge_repo.get_file(first_file_id)
            assert len(file.corresponding_chunks) > 0
            with pytest.raises(DocumentIsNotInProcessingPhaseError):
                file.assert_document_is_in_processing_phase()
            assert (
                file.status
                == UploadedTextLikeFileProcessingStatus.stored_preprocessed_chunked_and_embeddings_stored_in_vectorstore
            )

        number_of_chunks_in_vector_store = len(
            fake_vector_store.return_first_thousand_embeddings_of_file_id(first_file_id)
        )
        assert number_of_chunks_in_vector_store == len(file.corresponding_chunks)
