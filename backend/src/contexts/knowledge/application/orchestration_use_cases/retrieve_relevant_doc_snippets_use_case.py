from uuid import UUID

from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.vector_store_port import (
    TextChunkReturnDTO,
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.domain.models import TextFileChunk, UploadedTextLikeFile
from src.contexts.shared.typing_aliases import Factory


def retrieve_doc_snippets(
    vector_store: VectorStorePortTextChunks,
    cgpt_permission_checker: CgptPermissionCheckerPort,
    embedding_generator: EmbeddingGeneratorPort,
    knowledge_uow_factory: Factory[KnowledgeUOW],
    query_text: str,
    cgpt_id: str,
) -> list[str]:
    cgpt_permission_checker.assure_user_has_access_to_cgpts(cgpt_ids_to_check=[cgpt_id])
    with knowledge_uow_factory() as uow:
        file_ids = uow.knowledge_repo.get_file_ids_of_cgpt(cgpt_id=cgpt_id)
    embedding = embedding_generator.create_embeddings_for_texts(texts=[query_text])[0]
    num_snippets_to_query_vector_store_for = (
        UploadedTextLikeFile.NUM_EXPECTED_CHUNKS_FOR_POST_PROCESSING
    )
    nearest_chunkids_with_score: list[TextChunkReturnDTO] = (
        vector_store.return_relevant_text_snippets_ids_and_text(
            embedding_to_match=embedding,
            file_ids_to_include_in_filter=file_ids,
            max_snippets=num_snippets_to_query_vector_store_for,
        )
    )
    with knowledge_uow_factory() as uow:
        nearest_chunks: set[TextFileChunk] = (
            uow.knowledge_repo.get_chunks_assert_all_unique_and_exist(
                ids=[
                    id_and_score.id_of_chunk
                    for id_and_score in nearest_chunkids_with_score
                ]
            )
        )
    nearest_chunks_by_id: dict[UUID, TextFileChunk] = {
        chunk.id: chunk for chunk in nearest_chunks
    }

    nearest_chunks_with_score: list[tuple[TextFileChunk, float]] = [
        (
            nearest_chunks_by_id[id_and_score.id_of_chunk],
            id_and_score.score,
        )
        for id_and_score in nearest_chunkids_with_score
    ]
    auto_merged_nearest_chunks_ids = (
        UploadedTextLikeFile.post_process_retrieved_chunks_return_selected_chunk_ids(
            retrieved_chunks_with_score_from_vector_store=nearest_chunks_with_score
        )
    )
    with knowledge_uow_factory() as uow:
        auto_merged_chunks: set[TextFileChunk] = (
            uow.knowledge_repo.get_chunks_assert_all_unique_and_exist(
                ids=auto_merged_nearest_chunks_ids
            )
        )
    text_of_nearest_chunks = [chunk.text_content for chunk in auto_merged_chunks]
    return text_of_nearest_chunks
