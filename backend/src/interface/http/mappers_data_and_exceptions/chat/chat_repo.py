from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.chat_repo import (
    ConversationNotFoundError,
    TemporaryConvRepoError,
)


def register_exception_handlers_chat_repo_port(app: FastAPI) -> None:
    @app.exception_handler(TemporaryConvRepoError)
    async def _tbd(_, exc: TemporaryConvRepoError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unspecified error happened when retreiving chat data"
            },
        )

    @app.exception_handler(ConversationNotFoundError)
    async def _not_found(_, exc: ConversationNotFoundError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"Conversation was not found{getattr(exc, 'args', [''])[0]}"
            },
        )
