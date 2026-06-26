from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.vector_store_port import (
    FileIdsToIncludeMustNotBeEmptyError,
)


def register_exception_handlers_vector_store_port(app: FastAPI) -> None:
    @app.exception_handler(FileIdsToIncludeMustNotBeEmptyError)
    async def _not_found(_, exc: FileIdsToIncludeMustNotBeEmptyError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "No files associated with this cgpt to use for rag"},
        )
