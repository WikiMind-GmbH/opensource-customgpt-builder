from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session

from src.contexts.knowledge.application.ports.knowledge_repo import (
    CantCreateFileThatAlreadyExistsError,
    ChunkIdsAreNotUniqueError,
    ChunkNotFoundError,
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
            raise FileDoesNotExistError(f"No file exists with id {file_id}")
        return result

    def get_file_ids_of_cgpt(self, cgpt_id: str) -> list[UUID]:
        # stmt = select(CgptPermissionsToFile.file_id
        # # stmt = select(cgpt_permissions_to_files.c.file_id,
        # ).where(cgpt_permissions_to_files.c.cgpt_id ==cgpt_id)
        # file_ids = self.session.scalars(
        #     stmt
        # ).all()
        # return file_ids
        stmt = select(cgpt_permissions_to_files.c.file_id).where(
            cgpt_permissions_to_files.c.cgpt_id == cgpt_id
        )
        return list(self.session.scalars(stmt).all())

    def get_chunks_assert_all_unique_and_exist(
        self, ids: list[UUID]
    ) -> set[TextFileChunk]:
        if len(set(ids)) != len(ids):
            raise ChunkIdsAreNotUniqueError(
                f"Chunk lookup requires unique ids, received {ids}"
            )

        stmt = select(TextFileChunk).where(text_chunks_of_files.c._id.in_(ids))
        chunks = set(self.session.scalars(stmt).all())
        if len(chunks) != len(ids):
            found_ids = {chunk.id for chunk in chunks}
            missing_ids = [chunk_id for chunk_id in ids if chunk_id not in found_ids]
            raise ChunkNotFoundError(f"No chunks exist with ids {missing_ids}")

        return chunks

    def check_if_hash_already_exists(self, hash: str) -> bool:
        stmt = select(
            uploaded_text_like_file.c._id,
        ).where(uploaded_text_like_file.c._hash_of_raw_file == hash)
        rows = self.session.execute(stmt).all()
        if len(rows) > 0:
            return True
        return False

    def get_chunks_of_document(self, file_id: UUID) -> list[TextFileChunk]:
        stmt = select(TextFileChunk).where(
            text_chunks_of_files.c._corresponding_text_file_id == file_id
        )
        chunks = self.session.scalars(
            stmt
        ).all()  # scalars() unwraps the first selected value from each SQLAlchemy Row.
        if len(chunks) == 0:
            raise NoChunksExistForThisFileIDErrror(
                f"No chunks exist for file id {file_id}"
            )
        return list(chunks)

    def create_new_file_if_hash_doesnt_exist_yet(
        self, filename: str, hash: str, file_type: TextFileTypeEnum
    ) -> UploadedTextLikeFile:
        stmt = select(UploadedTextLikeFile).where(
            uploaded_text_like_file.c._hash_of_raw_file == hash
        )
        result = self.session.execute(stmt).all()
        if len(result) > 0:
            raise CantCreateFileThatAlreadyExistsError(
                f"A file with hash {hash} already exists"
            )

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
        except NoResultFound as exc:
            raise FileDoesNotExistError(
                f"No file exists with hash {hash_of_file}"
            ) from exc
        except MultipleResultsFound as exc:
            raise InvalidDatabaseStateError(
                f"More than one file exists with hash {hash_of_file}"
            ) from exc
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
