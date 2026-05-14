from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.ports.knowledge_repo import (
    CantCreateFileThatAlreadyExistsError,
    FileDoesNotExistError,
    InvalidDatabaseStateError,
    KnowledgeRepo,
    NoChunksExistForThisFileIDErrror,
)
from src.contexts.knowledge.domain.models import (
    CgptPermissionsToFile,
    TextFileChunk,
    TextFileTypeEnum,
    UploadedTextLikeFile,
)
from src.contexts.knowledge.infrastructure.db.orm import (
    cgpt_permissions_to_files,
    text_chunks_of_files,
    uploaded_text_like_file,
)


class SQLAlchemyKnowledgeRepository(KnowledgeRepo):
    def __init__(self, session: Session):
        self.session = session

    def get_file(self, file_id: UUID) -> UploadedTextLikeFile:
        result = self.session.get(UploadedTextLikeFile, file_id)
        if result is None:
            raise FileDoesNotExistError
        return result

    def get_chunks_of_document(self, file_id: UUID) -> list[TextFileChunk]:
        stmt = select(TextFileChunk).where(
            text_chunks_of_files.c._corresponding_text_file_id == file_id
        )
        chunks = self.session.scalars(
            stmt
        ).all()  # scalars() unwraps the first selected value from each SQLAlchemy Row.
        if len(chunks) == 0:
            raise NoChunksExistForThisFileIDErrror
        return list(chunks)

    def create_new_file_if_hash_doesnt_exist_yet(
        self, filename: str, hash: str, file_type: TextFileTypeEnum
    ) -> UploadedTextLikeFile:
        stmt = select(UploadedTextLikeFile).where(
            uploaded_text_like_file.c._hash_of_raw_file == hash
        )
        result = self.session.execute(stmt).all()
        if len(result) > 0:
            raise CantCreateFileThatAlreadyExistsError

        new_uploaded_text_like_file = UploadedTextLikeFile(
            name=filename, file_type=file_type, hash_of_raw_file=hash
        )
        self.session.add(new_uploaded_text_like_file)
        return new_uploaded_text_like_file

    def add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
        self, cgpt_ids: list[str], hash_of_file: str
    ) -> UUID:  # we use `hash_of_file` instead of `id` due to wanting to reinforce the idea that we only want to add permissions to a file based on identifying it with the hash
        stmt_get_id_of_file_with_hash = select(uploaded_text_like_file.c._id).where(
            uploaded_text_like_file.c._hash_of_raw_file == hash_of_file
        )
        try:
            result = self.session.execute(stmt_get_id_of_file_with_hash).one()
        except NoResultFound:
            raise FileDoesNotExistError
        except MultipleResultsFound:  #
            raise InvalidDatabaseStateError(
                "More than one file with the same hash exists"
            )
        id_of_file: UUID = result[0]
        stmt_permissions_of_this_file = select(CgptPermissionsToFile).where(
            cgpt_permissions_to_files.c.file_id == id_of_file
        )
        result = self.session.execute(stmt_permissions_of_this_file)
        cgpt_ids_with_permissions_already: list[str] = [row[0] for row in result.all()]
        cgpts_missing_permission_to_file: list[CgptPermissionsToFile] = [
            CgptPermissionsToFile(cgpt_id=cgpt_id, file_id=id_of_file)
            for cgpt_id in cgpt_ids
            if cgpt_id not in cgpt_ids_with_permissions_already
        ]
        self.session.add_all(cgpts_missing_permission_to_file)
        return id_of_file
