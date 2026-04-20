from openai import OpenAI

from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)


class EmbeddingGeneratorOpenAIAdapter(EmbeddingGeneratorPort):
    def __init__(self) -> None:
        self.embedding_model: str = "text-embedding-3-small"  # later as env
        self.client: OpenAI = OpenAI()

    def create_embedding_for_text(self, text: str) -> list[float]:
        response = self.client.embeddings.create(input=text, model=self.embedding_model)
        embedding_vector = response.data[0].embedding
        return embedding_vector

    def create_embeddings_for_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            input=texts, model=self.embedding_model
        )
        embedding_vectors = [embedding.embedding for embedding in response.data]
        return embedding_vectors
