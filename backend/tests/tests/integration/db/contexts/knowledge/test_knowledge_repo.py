from uuid import UUID, uuid4

import pytest
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.ports.knowledge_repo import (
    CantCreateFileThatAlreadyExistsError,
    FileDoesNotExistError,
    InvalidDatabaseStateError,
)
from src.contexts.knowledge.domain.models import TextFileTypeEnum
from src.contexts.knowledge.infrastructure.db.knowledge_repo_adapter import (
    SQLAlchemyKnowledgeRepository,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    cgpt_permissions_to_files,
    uploaded_text_like_file,
)
from src.contexts.shared.typing_aliases import Factory


def _create_uploadedfile_entry_commit_return_id(
    session: Session, hash: str, id_or_none_for_uuid: UUID | None = None
) -> UUID:
    id = id_or_none_for_uuid if id_or_none_for_uuid is not None else uuid4()
    session.execute(
        insert(uploaded_text_like_file).values(
            _id=id,
            _name="name",
            _file_type=TextFileTypeEnum.txt,
            _raw_file_is_stored=True,
            _transformed_text=None,
            _hash_of_raw_file=hash,
            _chunks_are_embedded=False,
            _chunks_are_embedded_and_added_to_vectorstore=False,
        )
    )
    session.commit()
    return id


def _create_permission_entry_commit(
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


def _return_all_cgpt_id_file_id_tuples_in_permission_table_with_file_id(
    file_id: UUID, session: Session
) -> list[tuple[str, UUID]]:
    stmt = select(
        cgpt_permissions_to_files.c.cgpt_id, cgpt_permissions_to_files.c.file_id
    ).where(cgpt_permissions_to_files.c.file_id == file_id)
    result = session.execute(stmt)
    list_of_tuples = [(row.cgpt_id, row.file_id) for row in result.all()]
    return list_of_tuples


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
        verification_repository = SQLAlchemyKnowledgeRepository(verification_session)
        fetched_conversation = verification_repository.get_file(file_id)
        assert fetched_conversation.id == file_id


def test_get_file_raises_when_missing(session_factory: Factory[Session]):
    with session_factory() as verification_session:
        verification_repository = SQLAlchemyKnowledgeRepository(verification_session)

        with pytest.raises(FileDoesNotExistError):
            verification_repository.get_file(uuid4())


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
        _create_uploadedfile_entry_commit_return_id(session=session, hash=hash)
        _create_uploadedfile_entry_commit_return_id(session=session, hash=hash)

    with session_factory() as multiple_files_with_this_hash_session:
        repo = SQLAlchemyKnowledgeRepository(multiple_files_with_this_hash_session)
        with pytest.raises(InvalidDatabaseStateError):
            repo.add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
                cgpt_ids=["S"], hash_of_file=hash
            )


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
        file_id = _create_uploadedfile_entry_commit_return_id(
            session=create_file_session, hash=hash
        )

    with session_factory() as create_previous_permissions_session:
        for cgpt_id in previous_cgpt_ids_added_to_file:
            _create_permission_entry_commit(
                session=create_previous_permissions_session,
                file_id=file_id,
                cgpt_id=cgpt_id,
            )
        all_permission_tuples_of_file_id = (
            _return_all_cgpt_id_file_id_tuples_in_permission_table_with_file_id(
                file_id=file_id, session=create_previous_permissions_session
            )
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
        all_permission_tuples_of_file_id = (
            _return_all_cgpt_id_file_id_tuples_in_permission_table_with_file_id(
                file_id=file_id, session=verification_session
            )
        )
        expected_permission_tuple_list_unordered = [
            (cgpt_id, file_id)
            for cgpt_id in set(cgpt_ids_of_request + previous_cgpt_ids_added_to_file)
        ]
        assert (
            all_permission_tuples_of_file_id.sort()
            == expected_permission_tuple_list_unordered.sort()
        )


def test_create_new_file_if_hash_doesnt_exist_yet_raises_when_hash_already_exists(
    session_factory: Factory[Session],
):
    hash = "hash"
    with session_factory() as session:
        _create_uploadedfile_entry_commit_return_id(session=session, hash=hash)
    with session_factory() as verification_session:
        verification_repository = SQLAlchemyKnowledgeRepository(verification_session)

        with pytest.raises(CantCreateFileThatAlreadyExistsError):
            verification_repository.create_new_file_if_hash_doesnt_exist_yet(
                filename="name", hash=hash, file_type=TextFileTypeEnum.txt
            )
