from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.knowledge_repo import (
    CantCreateFileThatAlreadyExistsError,
    ChunkIdsAreNotUniqueError,
    ChunkNotFoundError,
    FileDoesNotExistError,
    FileTypeNotSupportedError,
    InvalidDatabaseStateError,
    NoChunksExistForThisFileIDErrror,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="KnowledgeRepoPort")


def register_exception_handlers_knowledge_repo_port(app: FastAPI) -> None:
    @app.exception_handler(FileDoesNotExistError)
    async def _file_not_found(_, exc: FileDoesNotExistError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.warning("Knowledge repository file lookup failed: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )

    @app.exception_handler(CantCreateFileThatAlreadyExistsError)
    async def _file_already_exists(_, exc: CantCreateFileThatAlreadyExistsError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.info("Knowledge repository rejected duplicate file creation: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )

    @app.exception_handler(FileTypeNotSupportedError)
    async def _unsupported_file_type(_, exc: FileTypeNotSupportedError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.info("Knowledge repository rejected unsupported file type: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content={"detail": "The document type is not supported"},
        )

    @app.exception_handler(NoChunksExistForThisFileIDErrror)
    async def _no_chunks(_, exc: NoChunksExistForThisFileIDErrror):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.warning("Knowledge repository found no chunks for document: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )

    @app.exception_handler(ChunkNotFoundError)
    async def _chunk_not_found(_, exc: ChunkNotFoundError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.error("Knowledge repository chunk lookup was incomplete: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )

    @app.exception_handler(ChunkIdsAreNotUniqueError)
    async def _chunk_ids_not_unique(_, exc: ChunkIdsAreNotUniqueError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.error("Knowledge repository received duplicate chunk ids: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )

    @app.exception_handler(InvalidDatabaseStateError)
    async def _invalid_database_state(_, exc: InvalidDatabaseStateError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.error(
            "Knowledge repository reached an invalid database state: %s",
            exc,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )
