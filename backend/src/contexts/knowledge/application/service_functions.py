from fastapi import BackgroundTasks, UploadFile

from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
    UserHasNoPermissionForCgptOrTheyDontExist,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.file_storage_port import RawFileStorePort
from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    KnowledgeDBQueriesPort,
)
from src.contexts.knowledge.application.ports.knowledge_repo import (
    AddChunkEmbeddingsDTO,
)
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.pre_process_text_likes_port import (
    PreProcessTextLikesPort,
)
from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.domain.models import (
    TextFileChunk,
    TextFileTypeEnum,
    UnsupportedFileTypeError,
    UploadedTextLikeFile,
)
from src.interface.http.schemas.common_command import CommandResult


def upload_document_complete_workflow(
    uploadFile: UploadFile,  # ToDo: should migrate away from using this. As we want the service
    preProcessAdapter: PreProcessTextLikesPort,
    knowledge_uow: KnowledgeUOW,
    accessible_to_cgpts: list[str],
    cgpt_permissions_adapter: CgptPermissionCheckerPort,
    knowledge_db_queries_adapter: KnowledgeDBQueriesPort,
    file_storage_adapter: RawFileStorePort,
    background_tasks: BackgroundTasks,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
) -> CommandResult:
    # uow
    try:
        cgpt_permissions_adapter.assure_user_has_access_to_cgpts(accessible_to_cgpts)
    except UserHasNoPermissionForCgptOrTheyDontExist as e:
        raise e
    try:
        file_type, filename = (
            UploadedTextLikeFile.get_TextFileTypeEnum_from_filename_throw_error_if_not_supported(
                filename=uploadFile.filename
            )
        )
    except UnsupportedFileTypeError as e:
        raise e
    result = _upload_document_complete_workflow_after_further_validation(
        uploadFile,
        preProcessAdapter,
        knowledge_uow=knowledge_uow,
        accessible_to_cgpts=accessible_to_cgpts,
        file_type=file_type,
        knowledge_db_queries_adapter=knowledge_db_queries_adapter,
        filename=filename,
        file_storage_adapter=file_storage_adapter,
        background_tasks=background_tasks,
        vector_store_adapter=vector_store_adapter,
        embedding_generator_adapter=embedding_generator_adapter,
    )
    return result
    # if exception, e.g. no text was able to be recovered: rollback, throw exception notifying also client, ROLLBACK, delete file if it was stored


def _upload_document_complete_workflow_after_further_validation(
    uploadFile: UploadFile,
    preProcessAdapter: PreProcessTextLikesPort,
    knowledge_uow: KnowledgeUOW,
    accessible_to_cgpts: list[str],
    file_type: TextFileTypeEnum,
    knowledge_db_queries_adapter: KnowledgeDBQueriesPort,
    filename: str,
    file_storage_adapter: RawFileStorePort,
    background_tasks: BackgroundTasks,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
) -> CommandResult:
    file_contents: bytes = uploadFile.file.read()
    hash: str = UploadedTextLikeFile.calculate_hash_based_on_text_like_file_type(
        txt_like_file_type=file_type, content=file_contents
    )
    file_already_exists: bool = (
        knowledge_db_queries_adapter.check_if_hash_already_exists(hash=hash)
    )
    if file_already_exists:
        with knowledge_uow as uow:
            file_id = uow.knowledge_repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
                cgpt_ids=accessible_to_cgpts, hash_of_file=hash
            )
        return CommandResult(
            resource_id=str(file_id),
            message=f"cgpts {str(accessible_to_cgpts)} now have access to document with id {file_id}",
        )

    with knowledge_uow as uow:
        uploaded_file: UploadedTextLikeFile = (
            uow.knowledge_repo.create_new_file_if_hash_doesnt_exist_yet(
                file_bytes=file_contents,
                filename=filename,
                hash=hash,
                file_type=file_type,
            )
        )
        uow.knowledge_repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
            cgpt_ids=accessible_to_cgpts, hash_of_file=hash
        )
        file_storage_adapter.add_file(
            file_contents=file_contents, file_id=uploaded_file.id
        )
        uploaded_file.set_raw_file_was_stored()
        uow.commit()
    background_tasks.add_task(
        _preprocess_and_chunk_document_then_embedd,
        uploaded_file,
        knowledge_uow,
        preProcessAdapter,
        file_storage_adapter,
        vector_store_adapter,
        embedding_generator_adapter,
    )
    return CommandResult(
        resource_id=str(uploaded_file.id),
        message=f"Document {uploaded_file.id} is now uploaded and will be processed. It will be available for cgpts {str(accessible_to_cgpts)}",
    )


# def _preprocess_and_chunk_document(
#     uploaded_file: UploadedTextLikeFile,
#     knowledge_uow: KnowledgeUOW,
#     preProcessAdapter: PreProcessTextLikesPort,
#     file_storage_adapter: RawFileStorePort,
# ):
#     file_contents: bytes = file_storage_adapter.get_file(file_id=uploaded_file.id)
#     file_content_processed_to_string: str = (
#         preProcessAdapter.process_document_to_string_based_on_file_type(
#             uploadedTextLikeFile=uploaded_file, raw_file_content=file_contents
#         )
#     )
#     with knowledge_uow as uow:
#         uploaded_file = uow.knowledge_repo.get_file(uploaded_file.id)
#         uploaded_file.set_transformed_text(text=file_content_processed_to_string)
#         uow.commit()

#     chunks_of_document: list[TextFileChunk] = (
#         uploaded_file.create_chunks_from_raw_text()
#     )  # outside of uow -> not blocking the db pool; also: no relationships needed -> lazy loading should not be a problem

#     with knowledge_uow as setter_uow:
#         uploaded_file = setter_uow.knowledge_repo.get_file(uploaded_file.id)
#         uploaded_file.set_chunks(chunks_of_document)
#         setter_uow.commit()


def _preprocess_and_chunk_document_then_embedd(
    uploaded_file: UploadedTextLikeFile,
    knowledge_uow: KnowledgeUOW,
    preProcessAdapter: PreProcessTextLikesPort,
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
):
    file_contents: bytes = file_storage_adapter.get_file(file_id=uploaded_file.id)
    file_content_processed_to_string: str = (
        preProcessAdapter.process_document_to_string_based_on_file_type(
            uploadedTextLikeFile=uploaded_file, raw_file_content=file_contents
        )
    )
    with knowledge_uow as uow:
        uploaded_file = uow.knowledge_repo.get_file(uploaded_file.id)
        uploaded_file.set_transformed_text(text=file_content_processed_to_string)
        uow.commit()

    chunks_of_document: list[TextFileChunk] = (
        uploaded_file.create_chunks_from_raw_text()
    )  # outside of uow -> not blocking the db pool; also: no relationships needed -> lazy loading should not be a problem

    with knowledge_uow as setter_uow:
        uploaded_file = setter_uow.knowledge_repo.get_file(uploaded_file.id)
        uploaded_file.set_chunks(chunks_of_document)
        setter_uow.commit()

    _embedd_document_chunks_all_at_once(
        uploaded_file=uploaded_file,
        knowledge_uow=knowledge_uow,
        preProcessAdapter=preProcessAdapter,
        file_storage_adapter=file_storage_adapter,
        vector_store_adapter=vector_store_adapter,
        embedding_generator_adapter=embedding_generator_adapter,
        chunks_of_document=chunks_of_document,
    )


def _embedd_document_chunks_all_at_once(
    uploaded_file: UploadedTextLikeFile,
    knowledge_uow: KnowledgeUOW,
    preProcessAdapter: PreProcessTextLikesPort,
    file_storage_adapter: RawFileStorePort,
    vector_store_adapter: VectorStorePortTextChunks,
    embedding_generator_adapter: EmbeddingGeneratorPort,
    chunks_of_document: list[TextFileChunk],
):
    chunks_texts = [chunk.text for chunk in chunks_of_document]
    chunks_embeddings = embedding_generator_adapter.create_embeddings_for_texts(
        texts=chunks_texts
    )
    update_information_dto: AddChunkEmbeddingsDTO = AddChunkEmbeddingsDTO(
        file_id=uploaded_file.id,
        id_and_embedding_pairs_of_chunks=[
            (chunks_of_document[i].id, chunks_embeddings[i])
            for i in range(len(chunks_of_document))
        ],
    )
    with knowledge_uow as setter_uow:
        setter_uow.knowledge_repo.add_chunk_embeddings_update_file_and_chunks(
            update_information=update_information_dto
        )
    # save in vectorstore,
