# def retrieve_doc_snippets(
#     vector_store: VectorStorePortTextChunks,
#     cgpt_permission_checker: CgptPermissionCheckerPort,
#     embedding_generator: EmbeddingGeneratorPort,
#     knowledge_uow_factory: Factory[KnowledgeUOW],
#     query_text: str,
#     cgpt_id: str,
# ) -> list[str]:


from uuid import UUID, uuid4

import pytest
from sqlalchemy import insert
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.orchestration_use_cases.retrieve_relevant_doc_snippets_use_case import (
    retrieve_doc_snippets,
)
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
    UserHasNoPermissionForCgptOrTheyDontExist,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.vector_store_port import (
    ChunkEmbeddingAndMetadataDTO,
    MetadataDTO,
    ParentOrChildDTO,
    VectorStorePortTextChunks,
)
from src.contexts.knowledge.domain.models import (
    ChunkingStrategy,
    ParentOrChild,
    TextFileChunk,
    TextFileTypeEnum,
    UploadedTextLikeFileProcessingStatus,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    cgpt_permissions_to_files,
    text_chunks_of_files,
    uploaded_text_like_file,
)
from src.contexts.shared.typing_aliases import Factory


class _HelperFnxs:
    @staticmethod
    def create_uploadedfile_entry_commit_return_id(
        session: Session,
        hash: str,
        id_or_none_for_uuid: UUID | None = None,
        status: UploadedTextLikeFileProcessingStatus = (
            UploadedTextLikeFileProcessingStatus.raw_file_stored
        ),
    ) -> UUID:
        id = id_or_none_for_uuid if id_or_none_for_uuid is not None else uuid4()

        session.execute(
            insert(uploaded_text_like_file).values(
                _id=id,
                _name="name",
                _file_type=TextFileTypeEnum.txt,
                _status=status,
                _transformed_text=None,
                _hash_of_raw_file=hash,
            )
        )
        session.commit()

        return id

    @staticmethod
    def create_text_chunk_entry_commit_and_return_dto(
        *,
        knowledge_session: Session,
        file_id: UUID,
        embedding_dimension: int,
        text_content: str,
        parent_or_child: ParentOrChild = ParentOrChild.child,
        parent_id_if_child: UUID | None = None,
        chunking_strategy: ChunkingStrategy = (ChunkingStrategy.auto_merging),
    ) -> ChunkEmbeddingAndMetadataDTO:
        text_chunk = TextFileChunk(
            corresponding_text_file_id=file_id,
            text_content_of_chunk=text_content,
            chunking_strategy=chunking_strategy,
            hierarchy_level_of_chunk=parent_or_child,
            parent_id_if_child=parent_id_if_child,
        )

        knowledge_session.execute(
            insert(text_chunks_of_files).values(
                _id=text_chunk.id,
                _corresponding_text_file_id=text_chunk.corresponding_text_file_id,
                _text_content_of_chunk=text_chunk.text_content,
                _chunking_strategy=chunking_strategy,
                _hierarchy_level_of_chunk=text_chunk.is_parent_or_child,
                _parent_id_if_child=(
                    text_chunk.parent_id_if_child
                    if text_chunk.is_parent_or_child == ParentOrChild.child
                    else None
                ),
            )
        )
        knowledge_session.commit()

        return ChunkEmbeddingAndMetadataDTO(
            id_of_chunk=text_chunk.id,
            embedding_vector=[0.012 for _ in range(embedding_dimension)],
            metadata=MetadataDTO(
                parent_or_child_chunk=ParentOrChildDTO(
                    text_chunk.is_parent_or_child.value
                ),
                id_of_corresponding_file=text_chunk.corresponding_text_file_id,
                text_content=text_chunk.text_content,
            ),
        )

    @staticmethod
    def create_permission_entry_commit(
        session: Session, file_id: UUID, cgpt_id: str
    ) -> None:
        session.execute(
            insert(cgpt_permissions_to_files).values(
                _id=uuid4(),
                file_id=file_id,
                cgpt_id=cgpt_id,
            )
        )
        session.commit()
        return

    @staticmethod
    def create_random_file_with_permission_for_passed_cgpt_and_chunk_in_vectorstore(
        *,
        session: Session,
        vectorstore: VectorStorePortTextChunks,
        cgpt_id: str,
        embedding_dimension: int,
    ) -> ChunkEmbeddingAndMetadataDTO:
        file_id = _HelperFnxs.create_uploadedfile_entry_commit_return_id(
            session=session,
            hash=f"hash_{uuid4()}",
        )

        _HelperFnxs.create_permission_entry_commit(
            session=session,
            file_id=file_id,
            cgpt_id=cgpt_id,
        )

        parent_chunk = TextFileChunk(
            corresponding_text_file_id=file_id,
            text_content_of_chunk=f"random parent chunk content {uuid4()}",
            chunking_strategy=ChunkingStrategy.auto_merging,
            hierarchy_level_of_chunk=ParentOrChild.parent,
            parent_id_if_child=None,
        )

        session.execute(
            insert(text_chunks_of_files).values(
                _id=parent_chunk.id,
                _corresponding_text_file_id=parent_chunk.corresponding_text_file_id,
                _text_content_of_chunk=parent_chunk.text_content,
                _chunking_strategy=ChunkingStrategy.auto_merging,
                _hierarchy_level_of_chunk=parent_chunk.is_parent_or_child,
                _parent_id_if_child=None,
            )
        )
        session.commit()

        chunk_embedding_and_metadata_dto = ChunkEmbeddingAndMetadataDTO(
            id_of_chunk=parent_chunk.id,
            embedding_vector=[0.012 for _ in range(embedding_dimension)],
            metadata=MetadataDTO(
                parent_or_child_chunk=ParentOrChildDTO.parent,
                id_of_corresponding_file=parent_chunk.corresponding_text_file_id,
                text_content=parent_chunk.text_content,
            ),
        )

        vectorstore.add_chunks_with_corresponding_embeddings_and_metadata(
            chunk_embeddings_and_metadata_dtos=[chunk_embedding_and_metadata_dto],
        )

        return chunk_embedding_and_metadata_dto


class TestRetrieveDocSnippets:
    @staticmethod
    def test_raises_if_user_does_not_have_access_to_cgpt(
        fake_vector_store: VectorStorePortTextChunks,
        cgpt_permission_checker_false_return: CgptPermissionCheckerPort,
        fake_embedding_generator: EmbeddingGeneratorPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
    ):
        with pytest.raises(UserHasNoPermissionForCgptOrTheyDontExist):
            retrieve_doc_snippets(
                vector_store=fake_vector_store,
                cgpt_permission_checker=cgpt_permission_checker_false_return,
                embedding_generator=fake_embedding_generator,
                knowledge_uow_factory=knowledge_uow_factory,
                query_text="text",
                cgpt_id="",
            )

    @staticmethod
    def test_returns_nothing_if_cgpt_has_no_associated_docs(
        fake_vector_store: VectorStorePortTextChunks,
        cgpt_permission_checker_true_return: CgptPermissionCheckerPort,
        fake_embedding_generator: EmbeddingGeneratorPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
        embedding_dimension: int,
    ):
        returned_snippets = retrieve_doc_snippets(
            vector_store=fake_vector_store,
            cgpt_permission_checker=cgpt_permission_checker_true_return,
            embedding_generator=fake_embedding_generator,
            knowledge_uow_factory=knowledge_uow_factory,
            query_text="text",
            cgpt_id="",
        )
        assert len(returned_snippets) == 0

    @staticmethod
    def test_returns_at_least_one_snippet_if_cgpt_has_associated_docs(
        fake_vector_store: VectorStorePortTextChunks,
        cgpt_permission_checker_true_return: CgptPermissionCheckerPort,
        fake_embedding_generator: EmbeddingGeneratorPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
        session_factory: Factory[Session],
        embedding_dimension: int,
    ):
        this_cgpt_id = "1"
        with session_factory() as setup_session:
            _HelperFnxs.create_random_file_with_permission_for_passed_cgpt_and_chunk_in_vectorstore(
                session=setup_session,
                vectorstore=fake_vector_store,
                cgpt_id=this_cgpt_id,
                embedding_dimension=embedding_dimension,
            )

        returned_snippets = retrieve_doc_snippets(
            vector_store=fake_vector_store,
            cgpt_permission_checker=cgpt_permission_checker_true_return,
            embedding_generator=fake_embedding_generator,
            knowledge_uow_factory=knowledge_uow_factory,
            query_text="text",
            cgpt_id=this_cgpt_id,
        )
        assert len(returned_snippets) == 1

    @staticmethod
    def test_returns_only_snippets_of_provided_cgpt(
        fake_vector_store: VectorStorePortTextChunks,
        cgpt_permission_checker_true_return: CgptPermissionCheckerPort,
        fake_embedding_generator: EmbeddingGeneratorPort,
        knowledge_uow_factory: Factory[KnowledgeUOW],
        session_factory: Factory[Session],
        embedding_dimension: int,
    ):
        this_cgpt_id = "1"
        with session_factory() as setup_session:
            _HelperFnxs.create_random_file_with_permission_for_passed_cgpt_and_chunk_in_vectorstore(
                session=setup_session,
                vectorstore=fake_vector_store,
                cgpt_id=this_cgpt_id,
                embedding_dimension=embedding_dimension,
            )

        other_cgpt = "2"
        with session_factory() as setup_session:
            _HelperFnxs.create_random_file_with_permission_for_passed_cgpt_and_chunk_in_vectorstore(
                session=setup_session,
                vectorstore=fake_vector_store,
                cgpt_id=other_cgpt,
                embedding_dimension=embedding_dimension,
            )

        returned_snippets = retrieve_doc_snippets(
            vector_store=fake_vector_store,
            cgpt_permission_checker=cgpt_permission_checker_true_return,
            embedding_generator=fake_embedding_generator,
            knowledge_uow_factory=knowledge_uow_factory,
            query_text="text",
            cgpt_id=this_cgpt_id,
        )
        assert len(returned_snippets) == 1
