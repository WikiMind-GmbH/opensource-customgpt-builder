from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.pre_process_text_likes_port import (
    NotUTF8TxtFileError,
)


def register_query_exception_handlers_pre_processing_port(app: FastAPI) -> None:
    @app.exception_handler(NotUTF8TxtFileError)
    async def _invalid_file(_, exc: NotUTF8TxtFileError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content={"detail": "Only txt files encoded with utf-8 are supported"},
        )
