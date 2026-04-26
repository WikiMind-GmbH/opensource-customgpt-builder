import pytest

from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.infrastructure.adapters.embedding_generator_openai_adapter import (
    EmbeddingGeneratorOpenAIAdapter,
)


@pytest.fixture()
def embedding_generator() -> EmbeddingGeneratorPort:
    embedding_generator = EmbeddingGeneratorOpenAIAdapter()
    return embedding_generator
