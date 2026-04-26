from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)


def test_create_embeddings_for_texts_order_is_kept(
    embedding_generator: EmbeddingGeneratorPort,
):
    txt_1 = "We need sentences to embedd"
    txt_2 = "And they need to be different"
    txt_3 = "So we can test if order is kept"

    snippets = [txt_1, txt_2, txt_3]
    embeddings = embedding_generator.create_embeddings_for_texts(snippets)
    snippets.reverse()
    embeddings_of_reversed_snipptes_order = (
        embedding_generator.create_embeddings_for_texts(snippets)
    )

    embeddings.reverse()
    assert embeddings == embeddings_of_reversed_snipptes_order


def test_embedding_generator_returns_vectors_with_declared_dimension(
    embedding_generator: EmbeddingGeneratorPort,
) -> None:
    embeddings = embedding_generator.create_embeddings_for_texts(["hello", "world"])

    assert len(embeddings) == 2

    for embedding in embeddings:
        assert len(embedding) == embedding_generator.embedding_dimension
