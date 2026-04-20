from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import assert_never
from uuid import uuid4


class TextFileTypeEnum(StrEnum):
    # pdf = ".pdf"  # we will only read the text of pdfs for now - FUTURE: utilize the photos as well (treat them similar to singular photos?)
    # word = ".word"
    txt = ".txt"


# class ImageFileType(StrEnum):
#     jpg = ".jpg"
#     jpeg = ".jpeg"


# type FileType = TextFileTypeEnum  # | ImageFileType


class gpts_with_access:
    gpt_ids = list[str]


class UnsupportedFileTypeError(RuntimeError):
    "File type is not supported, only"


class InvalidInitializationError(RuntimeError):
    "Values passed to init would break invariant rules"


class DocumentIsAlreadyChunkedError(RuntimeError):
    "Document is already chunked. (All chunks are set at once)"


class InvalidTransformedTextError(RuntimeError):
    "Can't chunk unitialized transformed text or incorrectly transformed text (empty string)"


def createParentAndChildChunksFromTextCharacterSplit(
    full_text: str,
    corresponding_TextFile_id: str,
    parent_chunk_size: int = 3000,
    child_chunk_size: int = 600,
) -> list[TextFileChunk]:
    if len(full_text) == 0:
        raise RuntimeError(
            "Value passed is zero length string. This should not happen if this function is called- maybe incorrectly preprocessed doc"
        )

    chunking_stragegy = "Character Split Hyde"

    def create_parent_chunks(
        full_text: str,
        parent_chunk_size: int,
    ) -> list[TextFileChunk]:
        parent_chunks_text_only: list[str] = []
        num_parent_chunks = len(full_text) // parent_chunk_size + +(
            0 if len(full_text) % parent_chunk_size == 0 else 1
        )
        for parent_chunk_num in range(num_parent_chunks):
            parent_chunk = full_text[
                parent_chunk_size * parent_chunk_num : min(
                    parent_chunk_size * (parent_chunk_num + 1), len(full_text)
                )
            ]
            parent_chunks_text_only.append(parent_chunk)
        parent_chunks: list[TextFileChunk] = []
        for text_chunk in parent_chunks_text_only:
            chunk = TextFileChunk(
                corresponding_TextFile_id=corresponding_TextFile_id,
                text_content_of_chunk=text_chunk,
                chunking_stragegy=chunking_stragegy,
                hierarchy_level_of_chunk=ParentOrChild.parent,
            )
            parent_chunks.append(chunk)
        return parent_chunks

    def create_child_chunks(
        parent_Chunk: TextFileChunk, child_chunk_size: int
    ) -> list[TextFileChunk]:
        child_chunks_text_only: list[str] = []
        num_child_chunks = len(parent_Chunk.text) // child_chunk_size + +(
            0 if len(parent_Chunk.text) % child_chunk_size == 0 else 1
        )
        for child_chunk_num in range(num_child_chunks):
            child_chunk = parent_Chunk.text[
                child_chunk_num * child_chunk_size : min(
                    (child_chunk_num + 1) * child_chunk_size, len(parent_Chunk.text)
                )
            ]
            child_chunks_text_only.append(child_chunk)

        child_chunks: list[TextFileChunk] = []
        for text_chunk in child_chunks_text_only:
            chunk = TextFileChunk(
                corresponding_TextFile_id=corresponding_TextFile_id,
                text_content_of_chunk=text_chunk,
                chunking_stragegy=chunking_stragegy,
                hierarchy_level_of_chunk=ParentOrChild.child,
                parent_id_if_child=parent_Chunk.id,
            )
            child_chunks.append(chunk)
        return child_chunks

    parent_chunks = create_parent_chunks(
        full_text=full_text, parent_chunk_size=parent_chunk_size
    )
    child_chunks: list[TextFileChunk] = []
    for parent in parent_chunks:
        child_chunks = child_chunks + create_child_chunks(
            parent_Chunk=parent, child_chunk_size=child_chunk_size
        )
    return parent_chunks + child_chunks


# make it such that we can independently test this function


def createParentAndChildChunksFromTextRecursiveSplit(
    full_text: str,
) -> list[TextFileChunk]:
    raise NotImplementedError


class UploadedTextLikeFile:
    _id: str
    _name: str
    _file_type: TextFileTypeEnum

    _raw_file_is_stored: bool
    _transformed_text: str | None
    _corresponding_chunks: list[TextFileChunk] | None
    _hash_of_raw_file: str | None
    _chunks_are_embedded: bool
    _chunks_are_embedded_and_added_to_vectorstore: bool

    def __init__(
        self,
        name: str,
        file_type: TextFileTypeEnum,
        was_stored: bool = False,
        transformed_text: str | None = None,
        hash_of_raw_file: str | None = None,
    ) -> None:
        self._id = str(uuid4())
        self._name = name
        self._file_type = file_type
        self._raw_file_is_stored = was_stored
        self._transformed_text = transformed_text
        self._hash_of_raw_file = hash_of_raw_file
        self._corresponding_chunks = None
        self._chunks_are_embedded = False
        self._chunks_are_embedded_and_added_to_vectorstore = False

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def hash_of_raw_file(self):
        return self._hash_of_raw_file

    @property
    def file_type(self):
        return self._file_type

    @property
    def chunks_are_embedded(self):
        return self._chunks_are_embedded

    def set_chunks_are_embedded(self):
        self._chunks_are_embedded = True

    @property
    def chunks_are_embedded_and_added_to_vectorstore(self):
        return self._chunks_are_embedded_and_added_to_vectorstore

    def set_chunks_are_embedded_and_added_to_vectorstore(self):
        self._chunks_are_embedded_and_added_to_vectorstore = True

    def set_raw_file_was_stored(self):
        self._raw_file_is_stored = True

    def set_transformed_text(self, text: str):
        if text == "":
            raise InvalidInitializationError(
                "Zero length string can't be content of doc - something must have went wrong in the preprocessing step"
            )
        self._transformed_text = text

    @staticmethod
    def get_TextFileTypeEnum_from_filename_throw_error_if_not_supported(
        filename: str | None,
    ) -> tuple[TextFileTypeEnum, str]:
        if filename is None:
            raise UnsupportedFileTypeError(
                "Can't determine filetype based on filename if filename is not passed"
            )
        if filename.endswith(".txt"):
            return (TextFileTypeEnum.txt, filename)
        raise UnsupportedFileTypeError

    @staticmethod
    def calculate_hash_based_on_text_like_file_type(
        txt_like_file_type: TextFileTypeEnum, content: bytes
    ):
        match txt_like_file_type:
            case TextFileTypeEnum.txt:
                hash = hashlib.md5(content).hexdigest()
                return hash
            case _:
                assert_never(txt_like_file_type)

    def create_chunks_from_raw_text(  # due to not wanting to block the db connection pool, we must run this on a snapshot and update the object itself in a new uow
        self,
    ) -> list[
        TextFileChunk
    ]:  # I wanted to put this in a domain function instead of in an adapter because this is a core subdomain and the "how do we chunk" is central to the functionality
        if self._transformed_text is None or self.set_transformed_text == "":
            raise InvalidTransformedTextError
        if self._corresponding_chunks is not None:
            raise DocumentIsAlreadyChunkedError
        chunks = createParentAndChildChunksFromTextCharacterSplit(
            full_text=self._transformed_text,
            corresponding_TextFile_id=self._id,
        )
        return chunks

    def set_chunks(self, all_chunks: list[TextFileChunk]):
        if self._transformed_text is None or self.set_transformed_text == "":
            raise InvalidTransformedTextError
        if self._corresponding_chunks is not None:
            raise DocumentIsAlreadyChunkedError
        self._corresponding_chunks = all_chunks


class CgptPermissionsToFile:
    def __init__(self, cgpt_id: str, file_id: str):
        self.cgpt_id = cgpt_id
        self.file_id = file_id
        self._id = file_id + "|" + cgpt_id

    _id: str
    cgpt_id: str
    file_id: str


class ParentOrChild(StrEnum):
    parent = "parent"
    child = "child"


class TextFileChunk:
    def __init__(
        self,
        corresponding_TextFile_id: str,
        text_content_of_chunk: str,
        chunking_stragegy: str,
        hierarchy_level_of_chunk: ParentOrChild,
        parent_id_if_child: str | None = None,
    ) -> None:
        if text_content_of_chunk == "":
            raise InvalidInitializationError
        self.id = str(uuid4())
        self._corresponding_TextFile_id = corresponding_TextFile_id
        self._text_content_of_chunk = text_content_of_chunk
        self._chunking_stragegy = chunking_stragegy
        self._hierarchy_level_of_chunk = hierarchy_level_of_chunk
        self._parent_id_if_child = parent_id_if_child
        self._embedding_for_duplication_reason = None
        self._embedding_dimension = None

    _id: str
    _corresponding_TextFile_id: str
    _text_content_of_chunk: str
    _chunking_stragegy: str
    _hierarchy_of_chunk: ParentOrChild
    _parent_id_if_child: str | None
    _embedding_for_duplication_reason: list[float] | None
    _embedding_dimension: int | None

    @property
    def is_parent_or_child(self) -> ParentOrChild:
        return self._hierarchy_level_of_chunk

    @property
    def return_parent_id_if_this_is_child(self):
        if self._hierarchy_of_chunk == ParentOrChild.parent:
            raise RuntimeError(
                "Can't call this function on parent chunks, only child chunks"
            )
        return self._parent_id_if_child

    @property
    def text(self):
        return self._text_content_of_chunk

    def set_embedding(self, embedding: list[float], embedding_dim: int):
        self._embedding_dimension = embedding_dim
        self._embedding_for_duplication_reason = embedding

    def set_hierarchy(
        self, parent_or_child: ParentOrChild, parent_id: str | None = None
    ):
        if parent_or_child == ParentOrChild.parent and parent_id is not None:
            raise Exception(
                "Only child Chunks can have a parent_id - we have only two hierarchy levels"
            )
        if parent_or_child == ParentOrChild.parent and parent_id is None:
            self._hierarchy_of_chunk = parent_or_child
            return

        if parent_or_child == ParentOrChild.child and parent_id is None:
            raise Exception("Child chunks need an assosciated parent")
        if parent_or_child == ParentOrChild.child and parent_id is not None:
            self._hierarchy_level_of_chunk = parent_or_child
            self._parent_id_if_child = parent_id
            raise

    def set_parent_id_if_child(self, parent_id: str):
        if self._hierarchy_of_chunk == ParentOrChild.parent:
            raise Exception(
                "Only child Chunks can have a parent_id - we have only two hierarchy levels"
            )
        self._parent_id_if_child = parent_id
