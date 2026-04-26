from typing import Protocol

from attr import dataclass

from src.contexts.knowledge.domain.models import (
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


@dataclass
class AddChunkEmbeddingsDTO:
    file_id: str
    id_and_embedding_pairs_of_chunks: list[tuple[str, list[float]]]


class KnowledgeRepo(Protocol):
    def get_file(self, file_id: str) -> UploadedTextLikeFile: ...
    def create_new_file_if_hash_doesnt_exist_yet(
        self, filename: str, hash: str, file_type: TextFileTypeEnum
    ) -> UploadedTextLikeFile: ...

    def add_cgpt_to_file_permissions_if_not_done_already_return_file_id(
        self, cgpt_ids: list[str], hash_of_file: str
    ) -> str: ...  # we use `hash_of_file` instead of `id` due to wanting to reinforce the idea that we only want to add permissions to a file based on identifying it with the hash

    def add_chunk_embeddings_update_file_and_chunks(
        self,
        update_information: AddChunkEmbeddingsDTO,
    ) -> None: ...

    # def delete_file_from_cgpt_return_true_if_file_has_to_be_removed(
    #     self, cgpt_id: str, file_id: str
    # ) -> bool: ...

    # """
    # Two cases:
    # 1) file still has other cgpts connected -> we only remove the link to this file
    # 2) file had only this cgpt, now none -> we need to remove it from vector store and delete the domain model
    # """


# Next Up: go back to service function and see - why did we do this here
