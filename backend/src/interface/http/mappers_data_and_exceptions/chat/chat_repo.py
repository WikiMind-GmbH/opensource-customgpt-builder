from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.chat_repo import (
    ConversationNotFoundError,
    TemporaryConvRepoError,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="ChatRepoPort")


def register_exception_handlers_chat_repo_port(app: FastAPI) -> None:
    @app.exception_handler(TemporaryConvRepoError)
    async def _tbd(_, exc: TemporaryConvRepoError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.error("Conversation repository failed", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )

    @app.exception_handler(ConversationNotFoundError)
    async def _not_found(_, exc: ConversationNotFoundError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.warning(
            "Conversation repository found no matching conversation: %s", exc
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Conversation not found"},
        )
