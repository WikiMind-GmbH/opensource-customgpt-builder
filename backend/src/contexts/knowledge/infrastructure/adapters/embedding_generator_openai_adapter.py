from openai import OpenAI

from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)


class EmbeddingGeneratorOpenAIAdapter(EmbeddingGeneratorPort):
    def __init__(
        self,
        embedding_model: str = "text-embedding-3-small",
        embedding_dimension: int = 1536,
    ) -> None:
        self._embedding_model: str = embedding_model  # later as env
        self._embedding_dimension = embedding_dimension
        self._client: OpenAI = OpenAI()

    @property
    def embedding_dimension(self) -> int:
        return self._embedding_dimension

    def create_embeddings_for_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            input=texts, model=self._embedding_model
        )
        embedding_vectors = [embedding.embedding for embedding in response.data]
        return embedding_vectors
