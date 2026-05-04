from src.contexts.knowledge.domain.models import (
    TextFileChunk,
    create_parent_and_child_chunks_from_text_character_split,
)


def test_create_parent_and_child_chunks_from_text_character_split():
    test_text = "abcabca"
    text_chunks: list[TextFileChunk] = (
        create_parent_and_child_chunks_from_text_character_split(
            full_text=test_text,
            corresponding_text_file_id="id",
            parent_chunk_size=3,
            child_chunk_size=1,
        )
    )
    assert len(text_chunks) == 3 + 7
