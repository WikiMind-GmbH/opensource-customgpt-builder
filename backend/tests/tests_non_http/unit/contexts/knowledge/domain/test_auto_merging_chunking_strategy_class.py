from math import ceil
from uuid import UUID, uuid4

import pytest

from src.contexts.knowledge.domain.models import (
    ChunkingStrategy,
    ParentOrChild,
    TextFileChunk,
    _AutoMergingChunkingStrategy,  # pyright: ignore[reportPrivateUsage] - we must also test the private classes and methods
)


class TestCreateParentAndChildChunksFromTextCharacterSplit:
    @staticmethod
    def test_create_parent_and_child_chunks_from_text_character_split():
        test_text = "abcabca"
        overwrite_parent_chunk_size_for_tests = 3
        overwrite_child_chunk_size_for_tests = 1
        text_chunks: list[TextFileChunk] = (
            _AutoMergingChunkingStrategy.create_parent_and_child_chunks_from_text_character_split(
                full_text=test_text,
                corresponding_text_file_id=uuid4(),
                overwrite_parent_chunk_size_for_tests=overwrite_parent_chunk_size_for_tests,
                overwrite_child_chunk_size_for_tests=overwrite_child_chunk_size_for_tests,
            )
        )
        expected_child_chunks = len(test_text) / overwrite_child_chunk_size_for_tests
        expected_parent_chunks = ceil(
            len(test_text) / overwrite_parent_chunk_size_for_tests
        )
        assert len(text_chunks) == expected_child_chunks + expected_parent_chunks


def _chunk(
    *,
    chunk_id: UUID,
    hierarchy_level: ParentOrChild,
    parent_id_if_child: UUID | None = None,
) -> TextFileChunk:
    chunk = TextFileChunk(
        corresponding_text_file_id=uuid4(),
        text_content_of_chunk="some non-empty text",
        chunking_strategy=ChunkingStrategy.auto_merging,
        hierarchy_level_of_chunk=hierarchy_level,
        parent_id_if_child=parent_id_if_child,
    )

    # TextFileChunk generates IDs internally.
    # For deterministic assertions, tests pin the ID explicitly.
    chunk._id = chunk_id  # pyright: ignore[reportPrivateUsage] - private usage in tests is ok in this case

    return chunk


class TestAutoMergeChunks:
    def test_aggregates_minimum_number_of_children_to_parent_id_with_highest_child_score(
        self,
    ) -> None:
        parent_id = uuid4()
        child_1_id = uuid4()
        child_2_id = uuid4()

        child_1 = _chunk(
            chunk_id=child_1_id,
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=parent_id,
        )
        child_2 = _chunk(
            chunk_id=child_2_id,
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=parent_id,
        )

        result = _AutoMergingChunkingStrategy.auto_merge_chunks(
            [
                (child_1, 0.42),
                (child_2, 0.91),
            ]
        )

        assert result == [parent_id]

    def test_does_not_aggregate_if_less_than_minimum_number_of_children_for_same_parent(
        self,
    ) -> None:
        parent_id = uuid4()
        child_id = uuid4()

        child = _chunk(
            chunk_id=child_id,
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=parent_id,
        )

        result = _AutoMergingChunkingStrategy.auto_merge_chunks(
            [
                (child, 0.91),
            ]
        )

        assert result == [child_id]

    def test_parent_returned_only_once_when_direct_parent_and_aggregated_children_exist(
        self,
    ) -> None:
        parent_id = uuid4()

        parent = _chunk(
            chunk_id=parent_id,
            hierarchy_level=ParentOrChild.parent,
        )
        child_1 = _chunk(
            chunk_id=uuid4(),
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=parent_id,
        )
        child_2 = _chunk(
            chunk_id=uuid4(),
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=parent_id,
        )

        result = _AutoMergingChunkingStrategy.auto_merge_chunks(
            [
                (parent, 0.80),
                (child_1, 0.95),
                (child_2, 0.70),
            ]
        )

        assert result == [parent_id]

    def test_parent_score_is_highest_score_from_direct_parent_and_aggregated_children(
        self,
    ) -> None:
        high_scoring_parent_id = uuid4()
        lower_scoring_parent_id = uuid4()

        high_scoring_parent = _chunk(
            chunk_id=high_scoring_parent_id,
            hierarchy_level=ParentOrChild.parent,
        )
        lower_scoring_parent = _chunk(
            chunk_id=lower_scoring_parent_id,
            hierarchy_level=ParentOrChild.parent,
        )

        child_1 = _chunk(
            chunk_id=uuid4(),
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=high_scoring_parent_id,
        )
        child_2 = _chunk(
            chunk_id=uuid4(),
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=high_scoring_parent_id,
        )

        result = _AutoMergingChunkingStrategy.auto_merge_chunks(
            [
                (high_scoring_parent, 0.10),
                (lower_scoring_parent, 0.80),
                (child_1, 0.95),
                (child_2, 0.40),
            ]
        )

        assert result == [
            high_scoring_parent_id,
            lower_scoring_parent_id,
        ]

    def test_parent_and_child_chunks_are_both_counted_for_max_chunks_to_return(
        self,
    ) -> None:
        aggregated_parent_id = uuid4()

        child_1 = _chunk(
            chunk_id=uuid4(),
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=aggregated_parent_id,
        )
        child_2 = _chunk(
            chunk_id=uuid4(),
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=aggregated_parent_id,
        )

        parent_2_id = uuid4()
        parent_3_id = uuid4()
        parent_4_id = uuid4()
        parent_5_id = uuid4()
        parent_6_id = uuid4()

        parent_2 = _chunk(chunk_id=parent_2_id, hierarchy_level=ParentOrChild.parent)
        parent_3 = _chunk(chunk_id=parent_3_id, hierarchy_level=ParentOrChild.parent)
        parent_4 = _chunk(chunk_id=parent_4_id, hierarchy_level=ParentOrChild.parent)
        parent_5 = _chunk(chunk_id=parent_5_id, hierarchy_level=ParentOrChild.parent)
        parent_6 = _chunk(chunk_id=parent_6_id, hierarchy_level=ParentOrChild.parent)

        result = _AutoMergingChunkingStrategy.auto_merge_chunks(
            [
                (child_1, 1.00),
                (child_2, 0.99),
                (parent_2, 0.90),
                (parent_3, 0.80),
                (parent_4, 0.70),
                (parent_5, 0.60),
                (parent_6, 0.50),
            ]
        )

        assert result == [
            aggregated_parent_id,
            parent_2_id,
            parent_3_id,
            parent_4_id,
            parent_5_id,
        ]

        assert len(result) == _AutoMergingChunkingStrategy.NUM_MAX_CHUNKS_TO_RETURN

    def test_returns_highest_scoring_chunks_ordered_descending_after_merging(
        self,
    ) -> None:
        aggregated_parent_id = uuid4()

        child_1 = _chunk(
            chunk_id=uuid4(),
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=aggregated_parent_id,
        )
        child_2 = _chunk(
            chunk_id=uuid4(),
            hierarchy_level=ParentOrChild.child,
            parent_id_if_child=aggregated_parent_id,
        )

        parent_2_id = uuid4()
        parent_3_id = uuid4()

        parent_2 = _chunk(chunk_id=parent_2_id, hierarchy_level=ParentOrChild.parent)
        parent_3 = _chunk(chunk_id=parent_3_id, hierarchy_level=ParentOrChild.parent)

        result = _AutoMergingChunkingStrategy.auto_merge_chunks(
            [
                (parent_2, 0.70),
                (child_1, 0.30),
                (parent_3, 0.90),
                (child_2, 0.80),
            ]
        )

        assert result == [
            parent_3_id,
            aggregated_parent_id,
            parent_2_id,
        ]

    def test_raises_runtime_error_if_too_many_chunks_are_passed_for_post_processing(
        self,
    ) -> None:
        chunks_with_score = [
            (
                _chunk(
                    chunk_id=uuid4(),
                    hierarchy_level=ParentOrChild.parent,
                ),
                1.0 - index / 100,
            )
            for index in range(
                _AutoMergingChunkingStrategy.NUM_EXPECTED_CHUNKS_FOR_POST_PROCESSING + 1
            )
        ]

        with pytest.raises(RuntimeError):
            _AutoMergingChunkingStrategy.auto_merge_chunks(chunks_with_score)

    def test_allows_exactly_expected_number_of_chunks_for_post_processing(
        self,
    ) -> None:
        chunks_with_score = [
            (
                _chunk(
                    chunk_id=uuid4(),
                    hierarchy_level=ParentOrChild.parent,
                ),
                1.0 - index / 100,
            )
            for index in range(
                _AutoMergingChunkingStrategy.NUM_EXPECTED_CHUNKS_FOR_POST_PROCESSING
            )
        ]

        result = _AutoMergingChunkingStrategy.auto_merge_chunks(chunks_with_score)

        assert len(result) == _AutoMergingChunkingStrategy.NUM_MAX_CHUNKS_TO_RETURN
