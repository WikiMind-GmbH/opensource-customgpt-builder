from typing import Protocol
from uuid import UUID

from src.contexts.knowledge.domain.models import (
    TextFileChunk,
    TextFileTypeEnum,
    UploadedTextLikeFile,
)


class FileDoesNotExistError(RuntimeError):
    "No file with this id was found"


class CantCreateFileThatAlreadyExistsError(RuntimeError):
    "A file with the same hash already exists in the db, meaning that this file must already be in the db. Please just add the cgpt to the permission of this file instead."


class FileTypeNotSupportedError(RuntimeError):
    f"This file type is not supported. Only files ending with {str([value for value in TextFileTypeEnum])} are supported"


class InvalidDatabaseStateError(Exception):
    "An invalid database state was reached. Please check what happend"


class NoChunksExistForThisFileIDErrror(RuntimeError):
    "No chunks exist for this file id. maybe even file with this id does not exist -this is not checked necessarily"


class KnowledgeRepo(Protocol):
    def get_file(self, file_id: UUID) -> UploadedTextLikeFile: ...
    def get_chunks_of_document(self, file_id: UUID) -> list[TextFileChunk]: ...
    def create_new_file_if_hash_doesnt_exist_yet(
        self, filename: str, hash: str, file_type: TextFileTypeEnum
    ) -> UploadedTextLikeFile: ...

    def add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
        self, cgpt_ids: list[str], hash_of_file: str
    ) -> UUID: ...  # we use `hash_of_file` instead of `id` due to wanting to reinforce the idea that we only want to add permissions to a file based on identifying it with the hash

    # def delete_file_from_cgpt_return_true_if_file_has_to_be_removed(
    #     self, cgpt_id: str, file_id: str
    # ) -> bool: ...

    # """
    # Two cases:
    # 1) file still has other cgpts connected -> we only remove the link to this file
    # 2) file had only this cgpt, now none -> we need to remove it from vector store and delete the domain model
    # """


# Next Up: go back to service function and see - why did we do this here
