import pytest
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.ports.knowledge_repo import (
    FileDoesNotExistError,
)
from src.contexts.knowledge.domain.models import (
    TextFileTypeEnum,
    UploadedTextLikeFile,
)
from src.contexts.knowledge.infrastructure.db.knowledge_uow_adapter import (
    SQLAlchemyKnowledgeUOW,
)
from src.contexts.shared.typing_aliases import Factory


def test_uow_commit_persists(session_factory: Factory[Session]) -> None:
    file_hash = "hash"

    with SQLAlchemyKnowledgeUOW(session_factory) as uow:
        uploaded_file: UploadedTextLikeFile = (
            uow.knowledge_repo.create_new_file_if_hash_doesnt_exist_yet(
                filename="name",
                hash=file_hash,
                file_type=TextFileTypeEnum.txt,
            )
        )
        file_id = uploaded_file.id
        uow.commit()

    with SQLAlchemyKnowledgeUOW(session_factory) as uow2:
        got = uow2.knowledge_repo.get_file(file_id)

        assert got.id == file_id


def test_uow_commit_needs_to_be_done_manually(
    session_factory: Factory[Session],
) -> None:
    file_hash = "hash"

    with SQLAlchemyKnowledgeUOW(session_factory) as uow:
        uploaded_file: UploadedTextLikeFile = (
            uow.knowledge_repo.create_new_file_if_hash_doesnt_exist_yet(
                filename="name",
                hash=file_hash,
                file_type=TextFileTypeEnum.txt,
            )
        )
        file_id = uploaded_file.id

    with SQLAlchemyKnowledgeUOW(session_factory) as uow2:
        with pytest.raises(FileDoesNotExistError):
            uow2.knowledge_repo.get_file(file_id)


def test_uow_rollback_on_exception(session_factory: Factory[Session]) -> None:
    file_id: str | None = None
    file_hash = "hash"

    with pytest.raises(RuntimeError):
        with SQLAlchemyKnowledgeUOW(session_factory) as uow:
            uploaded_file = uow.knowledge_repo.create_new_file_if_hash_doesnt_exist_yet(
                filename="name",
                hash=file_hash,
                file_type=TextFileTypeEnum.txt,
            )
            file_id = uploaded_file.id

            raise RuntimeError("Error before exiting the uow should lead to rollback")

    assert file_id is not None

    with SQLAlchemyKnowledgeUOW(session_factory) as uow2:
        with pytest.raises(FileDoesNotExistError):
            uow2.knowledge_repo.get_file(file_id)


def test_uow_reinitializes_after_context_exit(
    session_factory: Factory[Session],
) -> None:
    uow = SQLAlchemyKnowledgeUOW(session_factory)

    with uow as entered_uow:
        assert entered_uow.knowledge_repo is not None

    assert getattr(uow, "_session") is None
    assert getattr(uow, "_sqla_knowledge_repo") is None
