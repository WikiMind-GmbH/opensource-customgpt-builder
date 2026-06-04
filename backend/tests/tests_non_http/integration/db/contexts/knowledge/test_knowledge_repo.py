from uuid import UUID, uuid4

import pytest
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.ports.knowledge_repo import (
    CantCreateFileThatAlreadyExistsError,
    ChunkIdsAreNotUniqueError,
    ChunkNotFoundError,
    FileDoesNotExistError,
    InvalidDatabaseStateError,
)
from src.contexts.knowledge.domain.models import (
    ChunkingStrategy,
    ParentOrChild,
    TextFileChunk,
    TextFileTypeEnum,
    UploadedTextLikeFileProcessingStatus,
)
from src.contexts.knowledge.infrastructure.db.knowledge_repo_adapter import (
    SQLAlchemyKnowledgeRepository,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    cgpt_permissions_to_files,
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

    # ToDo: test get_chunks_assert_all_unique_and_exist

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
    def return_all_cgpt_id_file_id_tuples_in_permission_table_with_file_id(
        file_id: UUID, session: Session
    ) -> list[tuple[str, UUID]]:
        stmt = select(
            cgpt_permissions_to_files.c.cgpt_id, cgpt_permissions_to_files.c.file_id
        ).where(cgpt_permissions_to_files.c.file_id == file_id)
        result = session.execute(stmt)
        list_of_tuples = [(row.cgpt_id, row.file_id) for row in result.all()]
        return list_of_tuples


class TestGetFile:
    @staticmethod
    def test_get_file_raises_when_missing(session_factory: Factory[Session]):
        with session_factory() as verification_session:
            verification_repository = SQLAlchemyKnowledgeRepository(
                verification_session
            )

            with pytest.raises(FileDoesNotExistError):
                verification_repository.get_file(uuid4())


class TestGetFileIdsOfCgpt:
    @staticmethod
    def test_get_file_ids_of_cgpt_returns_all_files_of_this_cgpt_and_none_of_others(
        session_factory: Factory[Session],
    ):
        target_cgpt_id = "target_cgpt"
        other_cgpt_id = "other_cgpt"

        with session_factory() as setup_session:
            target_file_id_1 = _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=setup_session,
                hash="hash_1",
            )
            target_file_id_2 = _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=setup_session,
                hash="hash_2",
            )
            other_file_id = _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=setup_session,
                hash="hash_3",
            )

        with session_factory() as setup_permissions_session:
            _HelperFnxs.create_permission_entry_commit(
                session=setup_permissions_session,
                file_id=target_file_id_1,
                cgpt_id=target_cgpt_id,
            )
            _HelperFnxs.create_permission_entry_commit(
                session=setup_permissions_session,
                file_id=target_file_id_2,
                cgpt_id=target_cgpt_id,
            )
            _HelperFnxs.create_permission_entry_commit(
                session=setup_permissions_session,
                file_id=other_file_id,
                cgpt_id=other_cgpt_id,
            )

        with session_factory() as verification_session:
            repository = SQLAlchemyKnowledgeRepository(verification_session)

            file_ids = repository.get_file_ids_of_cgpt(target_cgpt_id)

            assert set(file_ids) == {target_file_id_1, target_file_id_2}
            assert other_file_id not in file_ids


class TestGetChunksAssertAllUniqueAndExist:
    @staticmethod
    def test_get_chunks_assert_all_unique_and_exist_returns_existing_chunks(
        session_factory: Factory[Session],
    ):
        with session_factory() as setup_session:
            file_id = _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=setup_session,
                hash="hash_chunks_exist",
            )

            chunk_1 = TextFileChunk(
                corresponding_text_file_id=file_id,
                text_content_of_chunk="chunk 1",
                chunking_strategy=ChunkingStrategy.auto_merging,
                hierarchy_level_of_chunk=ParentOrChild.parent,
            )
            chunk_2 = TextFileChunk(
                corresponding_text_file_id=file_id,
                text_content_of_chunk="chunk 2",
                chunking_strategy=ChunkingStrategy.auto_merging,
                hierarchy_level_of_chunk=ParentOrChild.parent,
            )

            setup_session.add_all([chunk_1, chunk_2])
            setup_session.commit()

            chunk_1_id = chunk_1.id
            chunk_2_id = chunk_2.id

        with session_factory() as verification_session:
            repository = SQLAlchemyKnowledgeRepository(verification_session)

            chunks = repository.get_chunks_assert_all_unique_and_exist(
                ids=[chunk_1_id, chunk_2_id]
            )

            assert {chunk.id for chunk in chunks} == {chunk_1_id, chunk_2_id}

    @staticmethod
    def test_get_chunks_assert_all_unique_and_exist_raises_when_ids_are_not_unique(
        session_factory: Factory[Session],
    ):
        duplicated_chunk_id = uuid4()

        with session_factory() as verification_session:
            repository = SQLAlchemyKnowledgeRepository(verification_session)

            with pytest.raises(ChunkIdsAreNotUniqueError):
                repository.get_chunks_assert_all_unique_and_exist(
                    ids=[duplicated_chunk_id, duplicated_chunk_id]
                )

    @staticmethod
    def test_get_chunks_assert_all_unique_and_exist_raises_when_chunk_does_not_exist(
        session_factory: Factory[Session],
    ):
        with session_factory() as setup_session:
            file_id = _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=setup_session,
                hash="hash_some_chunk_missing",
            )

            existing_chunk = TextFileChunk(
                corresponding_text_file_id=file_id,
                text_content_of_chunk="existing chunk",
                chunking_strategy=ChunkingStrategy.auto_merging,
                hierarchy_level_of_chunk=ParentOrChild.parent,
            )

            setup_session.add(existing_chunk)
            setup_session.commit()

            existing_chunk_id = existing_chunk.id

        missing_chunk_id = uuid4()

        with session_factory() as verification_session:
            repository = SQLAlchemyKnowledgeRepository(verification_session)

            with pytest.raises(ChunkNotFoundError):
                repository.get_chunks_assert_all_unique_and_exist(
                    ids=[existing_chunk_id, missing_chunk_id]
                )


class TestCheckIfHashAlreadyExists:
    @staticmethod
    def test_check_if_hash_already_exists_retruns_true_for_existing_hash(
        session_factory: Factory[Session],
    ):
        with session_factory() as session:
            repository = SQLAlchemyKnowledgeRepository(session)
            created_file = repository.create_new_file_if_hash_doesnt_exist_yet(
                filename="name", hash="hash", file_type=TextFileTypeEnum.txt
            )
            file_hash = created_file.hash_of_raw_file
            session.commit()

        with session_factory() as verification_session:
            verification_repository = SQLAlchemyKnowledgeRepository(
                verification_session
            )
            hash_already_exists = verification_repository.check_if_hash_already_exists(
                file_hash
            )
            assert hash_already_exists

    @staticmethod
    def test_check_if_hash_already_exists_retruns_false_for_non_existing_hash(
        session_factory: Factory[Session],
    ):
        with session_factory() as verification_session:
            verification_repository = SQLAlchemyKnowledgeRepository(
                verification_session
            )
            hash_already_exists = verification_repository.check_if_hash_already_exists(
                "IamAhash"
            )
            assert not hash_already_exists


class TestCreateNewFileIfHashDoesntExistYet:
    @staticmethod
    def test_create_new_file_if_hash_doesnt_exist_yet_and_get_file_roundtrip(
        session_factory: Factory[Session],
    ):
        with session_factory() as session:
            repository = SQLAlchemyKnowledgeRepository(session)
            created_file = repository.create_new_file_if_hash_doesnt_exist_yet(
                filename="name", hash="hash", file_type=TextFileTypeEnum.txt
            )
            file_id = created_file.id
            session.commit()

        with session_factory() as verification_session:
            verification_repository = SQLAlchemyKnowledgeRepository(
                verification_session
            )
            fetched_conversation = verification_repository.get_file(file_id)
            assert fetched_conversation.id == file_id

    @staticmethod
    def test_create_new_file_if_hash_doesnt_exist_yet_raises_when_hash_already_exists(
        session_factory: Factory[Session],
    ):
        hash = "hash"
        with session_factory() as session:
            _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=session, hash=hash
            )
        with session_factory() as verification_session:
            verification_repository = SQLAlchemyKnowledgeRepository(
                verification_session
            )

            with pytest.raises(CantCreateFileThatAlreadyExistsError):
                verification_repository.create_new_file_if_hash_doesnt_exist_yet(
                    filename="name", hash=hash, file_type=TextFileTypeEnum.txt
                )


class TestAddCgptToFilePermissionsIfNotDoneAlreadyReturnFileId:
    @staticmethod
    def test_add_cgpt_to_file_permissions_raises_errors_if_zero_or_more_than_one_files_with_hash_exists(
        session_factory: Factory[Session],
    ):
        hash = "hash"
        with session_factory() as no_files_with_this_hash_session:
            repo = SQLAlchemyKnowledgeRepository(no_files_with_this_hash_session)
            with pytest.raises(FileDoesNotExistError):
                repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
                    cgpt_ids=["S"], hash_of_file=hash
                )

        with session_factory() as session:
            _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=session, hash=hash
            )
            _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=session, hash=hash
            )

        with session_factory() as multiple_files_with_this_hash_session:
            repo = SQLAlchemyKnowledgeRepository(multiple_files_with_this_hash_session)
            with pytest.raises(InvalidDatabaseStateError):
                repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
                    cgpt_ids=["S"], hash_of_file=hash
                )

    @staticmethod
    def test_add_cgpt_to_file_permissions_adds_exactly_missing_pairs(
        session_factory: Factory[Session],
    ):
        """
        Setup:
        Creates a file and give initial list of cgpts permission to utilize it
        by adding entries to the permission table

        Test:
        check if utilizing the `add_cgpt_to_file_permissions_if_not_done_already_return_file_id`
        Adds the correct rows to the permission table:
        Add all missing pairs, remove none, no duplication cgpt_id,file_id tuples
        """
        previous_cgpt_ids_added_to_file = ["prev_1", "prev_2"]
        cgpt_ids_of_request = ["prev_1", "new_1", "new_2"]
        hash = "hash"
        with session_factory() as create_file_session:
            file_id = _HelperFnxs.create_uploadedfile_entry_commit_return_id(
                session=create_file_session, hash=hash
            )

        with session_factory() as create_previous_permissions_session:
            for cgpt_id in previous_cgpt_ids_added_to_file:
                _HelperFnxs.create_permission_entry_commit(
                    session=create_previous_permissions_session,
                    file_id=file_id,
                    cgpt_id=cgpt_id,
                )
            all_permission_tuples_of_file_id = _HelperFnxs.return_all_cgpt_id_file_id_tuples_in_permission_table_with_file_id(
                file_id=file_id, session=create_previous_permissions_session
            )
            assert all_permission_tuples_of_file_id == [
                (cgpt_id, file_id) for cgpt_id in previous_cgpt_ids_added_to_file
            ], (
                f"cgpts with permissions to file {file_id} should only be {previous_cgpt_ids_added_to_file}"
            )

        with session_factory() as test_session:
            repo = SQLAlchemyKnowledgeRepository(test_session)
            repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
                cgpt_ids=cgpt_ids_of_request, hash_of_file=hash
            )
            test_session.commit()
        with session_factory() as verification_session:
            all_permission_tuples_of_file_id = _HelperFnxs.return_all_cgpt_id_file_id_tuples_in_permission_table_with_file_id(
                file_id=file_id, session=verification_session
            )
            expected_permission_tuple_list_unordered = [
                (cgpt_id, file_id)
                for cgpt_id in set(
                    cgpt_ids_of_request + previous_cgpt_ids_added_to_file
                )
            ]
            assert (
                all_permission_tuples_of_file_id.sort()
                == expected_permission_tuple_list_unordered.sort()
            )
