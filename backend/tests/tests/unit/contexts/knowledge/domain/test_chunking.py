from src.contexts.knowledge.domain.models import (
    createParentAndChildChunksFromTextCharacterSplit,
)


def test_createParentAndChildChunksFromTextCharacterSplit():
    test_text = "abcabca"
    text_chunks = createParentAndChildChunksFromTextCharacterSplit(
        full_text=test_text,
        corresponding_TextFile_id="id",
        parent_chunk_size=3,
        child_chunk_size=1,
    )
    assert len(text_chunks) == 3 + 7
