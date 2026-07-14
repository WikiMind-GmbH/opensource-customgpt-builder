from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.vector_store_port import (
    FileIdsToIncludeMustNotBeEmptyError,
    InvalidEmbeddingDimension,
    NoSnippetsForPassedFileIdsExistError,
    NotFoundError,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="VectorStorePort")


def register_exception_handlers_vector_store_port(app: FastAPI) -> None:
    @app.exception_handler(FileIdsToIncludeMustNotBeEmptyError)
    async def _invalid_data(_, exc: FileIdsToIncludeMustNotBeEmptyError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.info("Vector store query rejected an empty file id filter")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "At least one file id must be supplied"},
        )

    @app.exception_handler(NotFoundError)
    async def _not_found(_, exc: NotFoundError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.warning("Vector store found no matching resource: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )

    @app.exception_handler(NoSnippetsForPassedFileIdsExistError)
    async def _no_snippets(_, exc: NoSnippetsForPassedFileIdsExistError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.info("Vector store found no snippets for the supplied file ids")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "No relevant document content was found"},
        )

    @app.exception_handler(InvalidEmbeddingDimension)
    async def _invalid_embedding_dimension(_, exc: InvalidEmbeddingDimension):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.error("Invalid embedding dimension used internally", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )
