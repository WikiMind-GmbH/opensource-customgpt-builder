from typing import Protocol

# @dataclass
# class EmbeddingsDTO:
#     text: str
#     embedding: list[list[float]]


class EmbeddingGeneratorPort(Protocol):
    @property
    def embedding_dimension(self) -> int:
        """Dimension of every embedding vector produced by this generator."""
        ...

    def create_embeddings_for_texts(self, texts: list[str]) -> list[list[float]]:
        """Create one embedding vector per input text."""
        ...
