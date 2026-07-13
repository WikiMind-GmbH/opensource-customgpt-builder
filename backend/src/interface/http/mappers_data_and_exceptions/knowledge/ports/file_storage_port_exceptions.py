from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.file_storage_port import FileNotFoundError
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="FileStoragePort")


def register_exception_handlers_file_storage_port(app: FastAPI) -> None:
    @app.exception_handler(FileNotFoundError)
    async def _not_found(_, exc: FileNotFoundError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.warning("File storage found no matching file: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )
