from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import assert_never
from uuid import UUID, uuid4


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


class DocumentIsNotInProcessingPhaseError(RuntimeError):
    "The document is not in the processing phase. The processing phase ranges from after the document has been stored and finishes after its embeddings have been stored in the vectordb"


class InvalidStateTransitionError(RuntimeError):
    "Invalid state transition"


class ParentOrChild(StrEnum):
    parent = "parent"
    child = "child"


class ChunkingStrategy(StrEnum):
    auto_merging = "Parent with children auto merging"


class AbsoluteMatchStrengthOfRetrievedSnippet(StrEnum):
    """How close is this snippet to the query in absolute terms?

    VERY_STRONG:
    The absolute similarity score is very high for this embedding model and corpus.

    STRONG:
        The score is high enough to plausibly represent semantic relevance.

    WEAK:
        The score is low or borderline.

    VERY_WEAK:
    The score is so low that the snippet is probably not useful.
    """

    VERY_STRONG = "very_strong"
    STRONG = "strong"
    WEAK = "weak"
    VERY_WEAK = "very_weak"


class ResultDistinctivenessOfRetrievedSnippet(StrEnum):
    """

    How special is this snippet compared to the corpus/background and the retrieved candidate set?
    a) contrast against random sampling distribution
    b) contrast against top-k distribution

    CLEAR_OUTLIER:
    The snippet is far above the random background distribution and clearly separated from nearby top-k candidates.

    DISTINCT:
        The snippet is meaningfully above background and has some separation from comparable candidates.

    COMPETITIVE:
        The snippet is above background, but many top-k candidates are similarly close.

    INDISTINCT:
    The snippet is not meaningfully separated from the background or from other top-k candidates.
    """

    CLEAR_OUTLIER = "clear_outlier"
    DISTINCT = "distinct"
    COMPETITIVE = "competitive"
    INDISTINCT = "indistinct"


class _AutoMergingChunkingStrategy:
    CHILD_CHUNK_SIZE: int = 500
    PARENT_CHUNK_SIZE: int = 3000
    MIN_CHILDREN_TO_INCLUDE_PARENT: int = 2
    NUM_EXPECTED_CHUNKS_FOR_POST_PROCESSING: int = 10
    NUM_MAX_CHUNKS_TO_RETURN: int = 5

    @classmethod
    def create_parent_and_child_chunks_from_text_character_split(
        cls,
        full_text: str,
        corresponding_text_file_id: UUID,
        overwrite_parent_chunk_size_for_tests: int | None = None,
        overwrite_child_chunk_size_for_tests: int | None = None,
    ) -> list[TextFileChunk]:
        child_chunk_size = (
            cls.CHILD_CHUNK_SIZE
            if overwrite_child_chunk_size_for_tests is None
            else overwrite_child_chunk_size_for_tests
        )
        parent_chunk_size = (
            cls.PARENT_CHUNK_SIZE
            if overwrite_parent_chunk_size_for_tests is None
            else overwrite_parent_chunk_size_for_tests
        )
        if overwrite_parent_chunk_size_for_tests is not None:
            parent_chunk_size = overwrite_parent_chunk_size_for_tests

        chunking_strategy = ChunkingStrategy.auto_merging

        if len(full_text) == 0:
            raise InvalidTransformedTextError(
                "Value passed is zero length string. This should not happen if this "
                "function is called. The document may have been incorrectly preprocessed."
            )

        if not child_chunk_size < parent_chunk_size:
            raise RuntimeError(
                "Invalid parameters passed, it must be the case that child_chunk_size < parent_chunk_size "
            )

        def create_parent_chunks(
            full_text: str,
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

        parent_chunks = create_parent_chunks(full_text=full_text)

        child_chunks: list[TextFileChunk] = []
        for parent in parent_chunks:
            child_chunks = child_chunks + create_child_chunks(
                parent_chunk=parent,
                child_chunk_size=child_chunk_size,
            )

        return parent_chunks + child_chunks

    @staticmethod
    def _get_directly_matched_parent_scores_by_id(
        retrieved_chunks_with_score_from_vector_store: list[
            tuple[TextFileChunk, float]
        ],
    ) -> dict[UUID, float]:
        return {
            chunk.id: score
            for chunk, score in retrieved_chunks_with_score_from_vector_store
            if chunk.is_parent_or_child is ParentOrChild.parent
        }

    @staticmethod
    def _group_child_hits_by_parent_id(
        retrieved_chunks_with_score_from_vector_store: list[
            tuple[TextFileChunk, float]
        ],
    ) -> dict[UUID, list[tuple[TextFileChunk, float]]]:
        child_hits_by_parent_id: dict[UUID, list[tuple[TextFileChunk, float]]] = {}

        for chunk, score in retrieved_chunks_with_score_from_vector_store:
            if chunk.is_parent_or_child is not ParentOrChild.child:
                continue

            parent_id = chunk.parent_id_if_child
            if parent_id is None:
                raise InvalidChunkHierarchyError("Child chunk missing parent id")

            child_hits_by_parent_id.setdefault(parent_id, []).append((chunk, score))

        return child_hits_by_parent_id

    @staticmethod
    def _select_chunk_scores_by_id_with_auto_merge(
        directly_matched_parent_scores_by_id: dict[UUID, float],
        child_hits_by_parent_id: dict[UUID, list[tuple[TextFileChunk, float]]],
        min_children_to_include_parent: int,
    ) -> dict[UUID, float]:
        selected_chunk_scores_by_id = directly_matched_parent_scores_by_id.copy()

        for parent_id, corresponding_child_hits in child_hits_by_parent_id.items():
            children_merge_to_parent = (
                len(corresponding_child_hits) >= min_children_to_include_parent
            )

            if children_merge_to_parent:
                scores_to_consider_for_merged_parent: list[float] = []
                child_scores = [score for _, score in corresponding_child_hits]
                scores_to_consider_for_merged_parent = (
                    scores_to_consider_for_merged_parent + child_scores
                )
                if parent_id in directly_matched_parent_scores_by_id.keys():
                    scores_to_consider_for_merged_parent.append(
                        directly_matched_parent_scores_by_id[parent_id]
                    )
                selected_chunk_scores_by_id[parent_id] = max(
                    scores_to_consider_for_merged_parent
                )
                continue

            for child_chunk, score in corresponding_child_hits:
                selected_chunk_scores_by_id[child_chunk.id] = score

        return selected_chunk_scores_by_id
        # make it such that we can independently test this function

    @classmethod
    def auto_merge_chunks(
        cls,
        retrieved_chunks_with_score_from_vector_store: list[
            tuple[TextFileChunk, float]
        ],
    ) -> list[UUID]:
        if (
            len(retrieved_chunks_with_score_from_vector_store)
            > cls.NUM_EXPECTED_CHUNKS_FOR_POST_PROCESSING
        ):
            raise RuntimeError(
                "Auto-merge post-processing expects the vector store to already limit "
                f"results to at most {cls.NUM_EXPECTED_CHUNKS_FOR_POST_PROCESSING} chunks, but got "
                f"{len(retrieved_chunks_with_score_from_vector_store)}."
            )

        directly_matched_parent_scores_by_id = (
            cls._get_directly_matched_parent_scores_by_id(
                retrieved_chunks_with_score_from_vector_store
            )
        )

        child_hits_by_parent_id = cls._group_child_hits_by_parent_id(
            retrieved_chunks_with_score_from_vector_store
        )

        selected_chunk_scores_by_id = cls._select_chunk_scores_by_id_with_auto_merge(
            directly_matched_parent_scores_by_id=directly_matched_parent_scores_by_id,
            child_hits_by_parent_id=child_hits_by_parent_id,
            min_children_to_include_parent=cls.MIN_CHILDREN_TO_INCLUDE_PARENT,
        )

        return [
            chunk_id
            for chunk_id, _score in sorted(
                selected_chunk_scores_by_id.items(),
                key=lambda item: item[1],
                reverse=True,
            )[: cls.NUM_MAX_CHUNKS_TO_RETURN]
        ]


# def create_parent_and_child_chunks_from_text_recursive_split(
#     full_text: str,
# ) -> list[TextFileChunk]:
#     raise NotImplementedError


class UploadedTextLikeFileProcessingStatus(StrEnum):
    created = "created"
    raw_file_stored = "raw_file_stored"
    stored_original_preprocessed_to_text = "stored_original_preprocessed_to_text"
    stored_original_and_preprocessed_and_chunked = (
        "stored_original_and_preprocessed_and_chunked"
    )
    stored_preprocessed_chunked_and_embeddings_stored_in_vectorstore = (
        "stored_preprocessed_chunked_and_embeddings_stored_in_vectorstore"
    )


# _PROCESSING_STATUS_ORDER: tuple[UploadedTextLikeFileProcessingStatus, ...] = (
#     UploadedTextLikeFileProcessingStatus.created,
#     UploadedTextLikeFileProcessingStatus.raw_file_stored,
#     UploadedTextLikeFileProcessingStatus.stored_original_preprocessed_to_text,
#     UploadedTextLikeFileProcessingStatus.stored_original_and_preprocessed_and_chunked,
#     UploadedTextLikeFileProcessingStatus.stored_preprocessed_chunked_and_embeddings_stored_in_vectorstore,
# )


# def _processing_status_index(
#     status: UploadedTextLikeFileProcessingStatus,
# ) -> int:
#     return _PROCESSING_STATUS_ORDER.index(status)


class NextNecessaryProcessingStep(StrEnum):
    extract_text = "extract_text"
    chunking = "chunking"
    create_and_store_embeddings = "create_and_store_embeddings"


class UploadedTextLikeFile:
    NUM_EXPECTED_CHUNKS_FOR_POST_PROCESSING = (
        _AutoMergingChunkingStrategy.NUM_EXPECTED_CHUNKS_FOR_POST_PROCESSING
    )
    _id: UUID
    _name: str
    _file_type: TextFileTypeEnum
    _status: UploadedTextLikeFileProcessingStatus

    _transformed_text: str | None
    _hash_of_raw_file: str
    _corresponding_chunks: list[TextFileChunk]
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.auto_merging

    def __init__(
        self,
        name: str,
        file_type: TextFileTypeEnum,
        hash_of_raw_file: str,
    ) -> None:
        self._id = uuid4()
        self._name = name
        self._file_type = file_type
        self._hash_of_raw_file = hash_of_raw_file
        self._transformed_text = None
        self._corresponding_chunks = []
        self._status = UploadedTextLikeFileProcessingStatus.created

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def hash_of_raw_file(self) -> str:
        return self._hash_of_raw_file

    @property
    def file_type(self) -> TextFileTypeEnum:
        return self._file_type

    @property
    def status(self) -> UploadedTextLikeFileProcessingStatus:
        return self._status

    @property
    def corresponding_chunks(self) -> list[TextFileChunk]:
        return self._corresponding_chunks

    # @property
    # def corresponding_child_chunks
    # def corresponding_parent_chunks

    # ---------------------------------------------------------------------------------------------------
    # Possible state transitions: either by explicit setting or as a side effect of another function
    def mark_raw_file_was_stored(self) -> None:
        """
        In contrast to other status transitions (raw_file_stored -> text_extracted) and (text_extracted -> chunked),
        the correctness of this transition depends on external systems (adapters with dbs).
        Instead of only on the domain model object and its properties.
        Thus the correctness is not guaranteed.
        """
        if self._status != UploadedTextLikeFileProcessingStatus.created:
            raise InvalidStateTransitionError
        self._status = UploadedTextLikeFileProcessingStatus.raw_file_stored

    def set_transformed_text(self, text: str) -> None:
        if self._status != UploadedTextLikeFileProcessingStatus.raw_file_stored:
            raise InvalidStateTransitionError
        if text == "":
            raise InvalidInitializationError(
                "Zero length string can't be content of doc. Something must have "
                "gone wrong in the preprocessing step."
            )

        self._transformed_text = text
        self._status = (
            UploadedTextLikeFileProcessingStatus.stored_original_preprocessed_to_text
        )

    def create_chunks_without_assigning_them_to_document_include_chunking_strategy(
        self,
    ) -> list[TextFileChunk]:
        # due to not wanting to block the db connection pool, we must run this on
        # a snapshot and update the object itself in a new uow.
        # I wanted to put this in a domain function instead of in an adapter because
        # this is a core subdomain and the "how do we chunk" is central to the
        # functionality.
        if self._transformed_text is None or self._transformed_text == "":
            raise InvalidTransformedTextError

        if (
            self._status
            != UploadedTextLikeFileProcessingStatus.stored_original_preprocessed_to_text
        ):
            raise InvalidStateTransitionError

        chunks = _AutoMergingChunkingStrategy.create_parent_and_child_chunks_from_text_character_split(
            full_text=self._transformed_text,
            corresponding_text_file_id=self._id,
        )

        return chunks

    def assign_chunks_created_with_domain_method_to_document(
        self,
        chunks_created_by_domain_model_function: list[TextFileChunk],
    ) -> None:
        # due to not wanting to block the db connection pool, we must run this on
        # a snapshot and update the object itself in a new uow.
        # I wanted to put this in a domain function instead of in an adapter because
        # this is a core subdomain and the "how do we chunk" is central to the
        # functionality.
        if self._corresponding_chunks != []:
            raise DocumentIsAlreadyChunkedError

        if self._transformed_text is None or self._transformed_text == "":
            raise InvalidTransformedTextError

        if chunks_created_by_domain_model_function == []:
            raise InvalidInitializationError("Cannot add an empty chunk list.")

        if (
            self._status
            != UploadedTextLikeFileProcessingStatus.stored_original_preprocessed_to_text
        ):
            raise InvalidStateTransitionError
        self._corresponding_chunks = chunks_created_by_domain_model_function
        self._status = UploadedTextLikeFileProcessingStatus.stored_original_and_preprocessed_and_chunked

    @staticmethod
    def post_process_retrieved_chunks_return_selected_chunk_ids(
        retrieved_chunks_with_score_from_vector_store: list[
            tuple[TextFileChunk, float]
        ],
    ) -> list[UUID]:
        return _AutoMergingChunkingStrategy.auto_merge_chunks(
            retrieved_chunks_with_score_from_vector_store=retrieved_chunks_with_score_from_vector_store
        )

    def mark_chunks_are_embedded_and_added_to_vectorstore(self) -> None:
        """
        In contrast to other status transitions (raw_file_stored -> text_extracted) and (text_extracted -> chunked),
        the correctness of this transition depends on external systems (adapters with dbs).
        Instead of only on the domain model object and its properties.
        Thus the correctness is not guaranteed.
        """
        if (
            self._status
            != UploadedTextLikeFileProcessingStatus.stored_original_and_preprocessed_and_chunked
        ):
            raise InvalidStateTransitionError

        self._status = UploadedTextLikeFileProcessingStatus.stored_preprocessed_chunked_and_embeddings_stored_in_vectorstore

    # ---------------------------------------------------------------------------------------------------
    # Methods to check availability to process

    def next_necessary_processing_step_if_in_processing_phase(
        self,
    ) -> NextNecessaryProcessingStep:
        if self.status == UploadedTextLikeFileProcessingStatus.raw_file_stored:
            return NextNecessaryProcessingStep.extract_text
        if (
            self.status
            == UploadedTextLikeFileProcessingStatus.stored_original_preprocessed_to_text
        ):
            return NextNecessaryProcessingStep.chunking
        if (
            self.status
            == UploadedTextLikeFileProcessingStatus.stored_original_and_preprocessed_and_chunked
        ):
            return NextNecessaryProcessingStep.create_and_store_embeddings
        raise DocumentIsNotInProcessingPhaseError(
            f"document is in incompatible phase {self.status}"
        )

    def assert_document_is_in_processing_phase(self) -> None:
        document_is_in_processing_phase = self.status in {
            UploadedTextLikeFileProcessingStatus.raw_file_stored,
            UploadedTextLikeFileProcessingStatus.stored_original_and_preprocessed_and_chunked,
            UploadedTextLikeFileProcessingStatus.stored_original_preprocessed_to_text,
        }
        if not document_is_in_processing_phase:
            raise DocumentIsNotInProcessingPhaseError(
                f"document is in incompatible phase {self.status}"
            )

    @property
    def document_is_completely_processed_and_marked_as_available_in_vector_db(
        self,
    ) -> bool:
        return (
            self.status
            == UploadedTextLikeFileProcessingStatus.stored_preprocessed_chunked_and_embeddings_stored_in_vectorstore
        )

    # ---------------------------------------------------------------------------------------------------
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


class CgptPermissionsToFile:
    _id: str
    cgpt_id: str
    file_id: UUID

    def __init__(self, cgpt_id: str, file_id: UUID) -> None:
        self.cgpt_id = cgpt_id
        self.file_id = file_id
        self._id = str(file_id) + "|" + cgpt_id


class TextFileChunk:
    _id: UUID
    _corresponding_text_file_id: UUID
    _text_content_of_chunk: str
    _chunking_strategy: ChunkingStrategy
    _hierarchy_level_of_chunk: ParentOrChild
    _parent_id_if_child: UUID | None

    def __init__(
        self,
        corresponding_text_file_id: UUID,
        text_content_of_chunk: str,
        chunking_strategy: ChunkingStrategy,
        hierarchy_level_of_chunk: ParentOrChild,
        parent_id_if_child: UUID | None = None,
    ) -> None:
        if text_content_of_chunk == "":
            raise InvalidInitializationError

        self._validate_chunk_hierarchy(
            parent_or_child=hierarchy_level_of_chunk,
            parent_id=parent_id_if_child,
        )

        self._id = uuid4()
        self._corresponding_text_file_id = corresponding_text_file_id
        self._text_content_of_chunk = text_content_of_chunk
        self._chunking_strategy = chunking_strategy
        self._hierarchy_level_of_chunk = hierarchy_level_of_chunk
        self._parent_id_if_child = parent_id_if_child

    @staticmethod
    def _validate_chunk_hierarchy(
        *,
        parent_or_child: ParentOrChild,
        parent_id: UUID | None,
    ) -> None:
        if parent_or_child == ParentOrChild.parent and parent_id is not None:
            raise InvalidChunkHierarchyError("Parent chunks cannot have a parent_id.")

        if parent_or_child == ParentOrChild.child and parent_id is None:
            raise InvalidChunkHierarchyError("Child chunks need an associated parent.")

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def is_parent_or_child(self) -> ParentOrChild:
        return self._hierarchy_level_of_chunk

    @property
    def parent_id_if_child(self) -> UUID | None:
        if self._hierarchy_level_of_chunk == ParentOrChild.parent:
            raise InvalidChunkHierarchyError(
                "Can't call this property on parent chunks, only child chunks."
            )

        return self._parent_id_if_child

    @property
    def corresponding_text_file_id(self) -> UUID:
        return self._corresponding_text_file_id

    @property
    def text_content(self) -> str:
        return self._text_content_of_chunk

    def set_hierarchy(
        self,
        parent_or_child: ParentOrChild,
        parent_id: UUID | None = None,
    ) -> None:
        self._validate_chunk_hierarchy(
            parent_or_child=parent_or_child,
            parent_id=parent_id,
        )

        self._hierarchy_level_of_chunk = parent_or_child
        self._parent_id_if_child = parent_id

    def set_parent_id_if_child(self, parent_id: UUID) -> None:
        if self._hierarchy_level_of_chunk == ParentOrChild.parent:
            raise InvalidChunkHierarchyError(
                "Only child chunks can have a parent_id. "
                "We have only two hierarchy levels."
            )

        self._parent_id_if_child = parent_id
