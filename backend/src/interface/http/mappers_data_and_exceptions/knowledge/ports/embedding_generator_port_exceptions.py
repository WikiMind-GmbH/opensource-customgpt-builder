from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingProviderError,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="EmbeddingGeneratorPort")


def register_exception_handlers_embedding_generator_port(app: FastAPI) -> None:
    @app.exception_handler(EmbeddingProviderError)
    async def _provider_error(_, exc: EmbeddingProviderError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.error("Embedding provider failed", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "Service temporarily unavailable"},
        )
