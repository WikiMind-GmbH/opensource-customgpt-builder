from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
    EmbeddingProviderError,
)


class DeterministicEmbeddingGeneratorAdapter(EmbeddingGeneratorPort):
    def __init__(self, embedding_dimension: int) -> None:
        if embedding_dimension <= 0:
            raise EmbeddingProviderError(
                f"Embedding dimension must be positive, got {embedding_dimension}."
            )

        self._embedding_dimension = embedding_dimension

    @property
    def embedding_dimension(self) -> int:
        return self._embedding_dimension

    def create_embeddings_for_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._create_embedding_for_text(text) for text in texts]

    def _create_embedding_for_text(self, text: str) -> list[float]:
        embedding = [0.0] * self._embedding_dimension

        if text == "":
            return embedding

        # Deterministic fake embedding for tests:
        # Convert every character to its Unicode number, sum those numbers,
        # and use modulo to map the sum into a valid vector index.
        # Then set exactly that one position to 1.0.
        #
        # This gives us:
        # - same text -> same vector
        # - correct vector dimension
        # - no external API call
        #
        # It is not semantically meaningful and different texts may map
        # to the same vector index, which is acceptable for simple tests.
        index = sum(ord(char) for char in text) % self._embedding_dimension
        embedding[index] = 1.0

        return embedding
