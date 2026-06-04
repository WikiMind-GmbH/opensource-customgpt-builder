from uuid import UUID

from src.contexts.knowledge.application.mappers import (
    MappersVectorStore,
    PreProcessTextLikesPortMapper,
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
    ChunkEmbeddingAndMetadataDTO,
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.domain.models import (
    NextNecessaryProcessingStep,
    TextFileChunk,
    UploadedTextLikeFile,
)
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
        file_already_exists: bool = uow.knowledge_repo.check_if_hash_already_exists(
            hash=hash
        )
    if file_already_exists:
        with knowledge_uow_factory() as uow:
            file_id = uow.knowledge_repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
                cgpt_ids=accessible_to_cgpts, hash_of_file=hash
            )
            return file_id

    with knowledge_uow_factory() as uow:
        uploaded_file: UploadedTextLikeFile = (
            uow.knowledge_repo.create_new_file_if_hash_doesnt_exist_yet(
                filename=file_name_with_ending,
                hash=hash,
                file_type=file_type,
            )
        )
        uow.commit()
        uow.knowledge_repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
            cgpt_ids=accessible_to_cgpts, hash_of_file=hash
        )
        file_storage_adapter.add_file(
            file_contents=file_bytes_content, file_id=uploaded_file.id
        )
        uploaded_file.mark_raw_file_was_stored()
        uow.commit()

    task_scheduler.add_task(
        preprocess_and_chunk_document_then_embedd,
        uploaded_file.id,
        knowledge_uow_factory,
        extract_text_from_document_adapter,
        file_storage_adapter,
        vector_store_adapter,
        embedding_generator_adapter,
    )
    return uploaded_file.id


def preprocess_and_chunk_document_then_embedd(
    uploaded_file_id: UUID,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    extract_text_from_document_adapter: ExtractTextFromDocumentPort,
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
):
    with knowledge_uow_factory() as uow:
        uploaded_file = uow.knowledge_repo.get_file(uploaded_file_id)
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
        embedd_document_chunks_all_at_once(
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
        embedd_document_chunks_all_at_once(
            uploaded_file_id=uploaded_file_id,
            knowledge_uow_factory=knowledge_uow_factory,
            vector_store_adapter=vector_store_adapter,
            embedding_generator_adapter=embedding_generator_adapter,
        )
    if (
        next_necessary_processing_step
        == NextNecessaryProcessingStep.create_and_store_embeddings
    ):
        embedd_document_chunks_all_at_once(
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
        uploaded_file.set_transformed_text(
            text=file_content_processed_to_string
        )  # <- this raises domain error if status is not expected status
        uow.commit()


def chunk_uploaded_file(
    uploaded_file_id: UUID,
    knowledge_uow_factory: Factory[KnowledgeUOW],
) -> None:
    with knowledge_uow_factory() as uow:
        uploaded_file = uow.knowledge_repo.get_file(uploaded_file_id)

    chunks_of_document: list[TextFileChunk] = (
        uploaded_file.create_chunks_without_assigning_them_to_document_include_chunking_strategy()
    )  # outside of uow -> not blocking the db pool; also: no relationships needed -> lazy loading should not be a problem

    with knowledge_uow_factory() as setter_uow:
        uploaded_file = setter_uow.knowledge_repo.get_file(uploaded_file.id)
        uploaded_file.assign_chunks_created_with_domain_method_to_document(
            chunks_of_document
        )
        setter_uow.commit()
    return


def embedd_document_chunks_all_at_once(
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
    vector_store_adapter.add_chunks_with_corresponding_embeddings_and_metadata(
        chunk_embeddings_and_metadata_dtos=chunk_embeddings_and_metadata_dtos
    )
    with knowledge_uow_factory() as uow:
        uploaded_file = uow.knowledge_repo.get_file(uploaded_file_id)
        uploaded_file.mark_chunks_are_embedded_and_added_to_vectorstore()
        uow.commit()
