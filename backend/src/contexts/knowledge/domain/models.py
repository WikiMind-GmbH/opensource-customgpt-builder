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


class UnsupportedFileTypeError(RuntimeError):
    "File type is not supported."


class InvalidChunkHierarchyError(RuntimeError):
    "Invalid parent/child chunk hierarchy."


class InvalidInitializationError(RuntimeError):
    "Values passed to init would break invariant rules."


class DocumentIsAlreadyChunkedError(RuntimeError):
    "Document is already chunked. Chunks must be set once."


class InvalidTransformedTextError(RuntimeError):
    "Can't chunk uninitialized transformed text or incorrectly transformed text."


class ParentOrChild(StrEnum):
    parent = "parent"
    child = "child"


def create_parent_and_child_chunks_from_text_character_split(
    full_text: str,
    corresponding_text_file_id: str,
    parent_chunk_size: int = 3000,
    child_chunk_size: int = 600,
) -> list[TextFileChunk]:
    if len(full_text) == 0:
        raise InvalidTransformedTextError(
            "Value passed is zero length string. This should not happen if this "
            "function is called. The document may have been incorrectly preprocessed."
        )

    if not child_chunk_size < parent_chunk_size and parent_chunk_size < len(full_text):
        raise RuntimeError(
            "Invalid parameters passed, it must be the case that child_chunk_size < parent_chunk_size and parent_chunk_size < len(full_text)"
        )

    chunking_strategy = "Character Split Hyde"

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
                    parent_chunk_size * (parent_chunk_num + 1),
                    len(full_text),
                )
            ]
            parent_chunks_text_only.append(parent_chunk)

        parent_chunks: list[TextFileChunk] = []
        for text_chunk in parent_chunks_text_only:
            chunk = TextFileChunk(
                corresponding_text_file_id=corresponding_text_file_id,
                text_content_of_chunk=text_chunk,
                chunking_strategy=chunking_strategy,
                hierarchy_level_of_chunk=ParentOrChild.parent,
            )
            parent_chunks.append(chunk)

        return parent_chunks

    def create_child_chunks(
        parent_chunk: TextFileChunk,
        child_chunk_size: int,
    ) -> list[TextFileChunk]:
        child_chunks_text_only: list[str] = []
        num_child_chunks = len(parent_chunk.text_content) // child_chunk_size + +(
            0 if len(parent_chunk.text_content) % child_chunk_size == 0 else 1
        )

        for child_chunk_num in range(num_child_chunks):
            child_chunk = parent_chunk.text_content[
                child_chunk_num * child_chunk_size : min(
                    (child_chunk_num + 1) * child_chunk_size,
                    len(parent_chunk.text_content),
                )
            ]
            child_chunks_text_only.append(child_chunk)

        child_chunks: list[TextFileChunk] = []
        for text_chunk in child_chunks_text_only:
            chunk = TextFileChunk(
                corresponding_text_file_id=corresponding_text_file_id,
                text_content_of_chunk=text_chunk,
                chunking_strategy=chunking_strategy,
                hierarchy_level_of_chunk=ParentOrChild.child,
                parent_id_if_child=parent_chunk.id,
            )
            child_chunks.append(chunk)

        return child_chunks

    parent_chunks = create_parent_chunks(
        full_text=full_text,
        parent_chunk_size=parent_chunk_size,
    )

    child_chunks: list[TextFileChunk] = []
    for parent in parent_chunks:
        child_chunks = child_chunks + create_child_chunks(
            parent_chunk=parent,
            child_chunk_size=child_chunk_size,
        )

    return parent_chunks + child_chunks


# make it such that we can independently test this function


def create_parent_and_child_chunks_from_text_recursive_split(
    full_text: str,
) -> list[TextFileChunk]:
    raise NotImplementedError


class UploadedTextLikeFile:
    _id: str
    _name: str
    _file_type: TextFileTypeEnum

    _raw_file_is_stored: bool
    _transformed_text: str | None
    _hash_of_raw_file: str | None
    _corresponding_chunks: list[TextFileChunk]
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
        self._corresponding_chunks = []
        self._chunks_are_embedded = False
        self._chunks_are_embedded_and_added_to_vectorstore = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> str:
        return self._id

    @property
    def hash_of_raw_file(self) -> str | None:
        return self._hash_of_raw_file

    @property
    def file_type(self) -> TextFileTypeEnum:
        return self._file_type

    @property
    def chunks_are_embedded(self) -> bool:
        return self._chunks_are_embedded

    def set_chunks_are_embedded(self) -> None:
        self._chunks_are_embedded = True

    @property
    def chunks_are_embedded_and_added_to_vectorstore(self) -> bool:
        return self._chunks_are_embedded_and_added_to_vectorstore

    def set_chunks_are_embedded_and_added_to_vectorstore(self) -> None:
        self._chunks_are_embedded_and_added_to_vectorstore = True

    def set_raw_file_was_stored(self) -> None:
        self._raw_file_is_stored = True

    def set_transformed_text(self, text: str) -> None:
        if text == "":
            raise InvalidInitializationError(
                "Zero length string can't be content of doc. Something must have "
                "gone wrong in the preprocessing step."
            )

        self._transformed_text = text

    @staticmethod
    def get_text_file_type_enum_from_filename_throw_error_if_not_supported(
        filename: str | None,
    ) -> tuple[TextFileTypeEnum, str]:
        if filename is None:
            raise UnsupportedFileTypeError(
                "Can't determine filetype based on filename if filename is not passed."
            )

        if filename.endswith(".txt"):
            return TextFileTypeEnum.txt, filename

        raise UnsupportedFileTypeError

    @staticmethod
    def calculate_hash_based_on_text_like_file_type(
        txt_like_file_type: TextFileTypeEnum,
        content: bytes,
    ) -> str:
        match txt_like_file_type:
            case TextFileTypeEnum.txt:
                content_hash = hashlib.sha256(content).hexdigest()
                return content_hash
            case _:
                assert_never(txt_like_file_type)

    def create_chunks_from_raw_text(
        self,
    ) -> list[TextFileChunk]:
        # due to not wanting to block the db connection pool, we must run this on
        # a snapshot and update the object itself in a new uow.
        #
        # I wanted to put this in a domain function instead of in an adapter because
        # this is a core subdomain and the "how do we chunk" is central to the
        # functionality.
        if self._transformed_text is None or self._transformed_text == "":
            raise InvalidTransformedTextError

        if self._corresponding_chunks != []:
            raise DocumentIsAlreadyChunkedError

        chunks = create_parent_and_child_chunks_from_text_character_split(
            full_text=self._transformed_text,
            corresponding_text_file_id=self._id,
        )

        return chunks

    def set_chunks(self, all_chunks: list[TextFileChunk]) -> None:
        if self._transformed_text is None or self._transformed_text == "":
            raise InvalidTransformedTextError

        if self._corresponding_chunks != []:
            raise DocumentIsAlreadyChunkedError

        self._corresponding_chunks = all_chunks


class CgptPermissionsToFile:
    _id: str
    cgpt_id: str
    file_id: str

    def __init__(self, cgpt_id: str, file_id: str) -> None:
        self.cgpt_id = cgpt_id
        self.file_id = file_id
        self._id = file_id + "|" + cgpt_id


class TextFileChunk:
    _id: str
    _corresponding_text_file_id: str
    _text_content_of_chunk: str
    _chunking_strategy: str
    _hierarchy_level_of_chunk: ParentOrChild
    _parent_id_if_child: str | None

    def __init__(
        self,
        corresponding_text_file_id: str,
        text_content_of_chunk: str,
        chunking_strategy: str,
        hierarchy_level_of_chunk: ParentOrChild,
        parent_id_if_child: str | None = None,
    ) -> None:
        if text_content_of_chunk == "":
            raise InvalidInitializationError

        self._validate_chunk_hierarchy(
            parent_or_child=hierarchy_level_of_chunk,
            parent_id=parent_id_if_child,
        )

        self._id = str(uuid4())
        self._corresponding_text_file_id = corresponding_text_file_id
        self._text_content_of_chunk = text_content_of_chunk
        self._chunking_strategy = chunking_strategy
        self._hierarchy_level_of_chunk = hierarchy_level_of_chunk
        self._parent_id_if_child = parent_id_if_child

    @staticmethod
    def _validate_chunk_hierarchy(
        *,
        parent_or_child: ParentOrChild,
        parent_id: str | None,
    ) -> None:
        if parent_or_child == ParentOrChild.parent and parent_id is not None:
            raise InvalidChunkHierarchyError("Parent chunks cannot have a parent_id.")

        if parent_or_child == ParentOrChild.child and parent_id is None:
            raise InvalidChunkHierarchyError("Child chunks need an associated parent.")

    @property
    def id(self) -> str:
        return self._id

    @property
    def is_parent_or_child(self) -> ParentOrChild:
        return self._hierarchy_level_of_chunk

    @property
    def parent_id_if_child(self) -> str | None:
        if self._hierarchy_level_of_chunk == ParentOrChild.parent:
            raise InvalidChunkHierarchyError(
                "Can't call this property on parent chunks, only child chunks."
            )

        return self._parent_id_if_child

    @property
    def corresponding_text_file_id(self) -> str:
        return self._corresponding_text_file_id

    @property
    def text_content(self) -> str:
        return self._text_content_of_chunk

    def set_hierarchy(
        self,
        parent_or_child: ParentOrChild,
        parent_id: str | None = None,
    ) -> None:
        self._validate_chunk_hierarchy(
            parent_or_child=parent_or_child,
            parent_id=parent_id,
        )

        self._hierarchy_level_of_chunk = parent_or_child
        self._parent_id_if_child = parent_id

    def set_parent_id_if_child(self, parent_id: str) -> None:
        if self._hierarchy_level_of_chunk == ParentOrChild.parent:
            raise InvalidChunkHierarchyError(
                "Only child chunks can have a parent_id. "
                "We have only two hierarchy levels."
            )

        self._parent_id_if_child = parent_id
