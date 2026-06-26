from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.domain.models import Conversation


def register_exception_handlers_chat_domain(
    app: FastAPI,
) -> None:
    @app.exception_handler(Conversation.CantUseRagIfNoCgptIsPassedError)
    async def _not_found(_, exc: Conversation.CantUseRagIfNoCgptIsPassedError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": f"Conversation not found: {getattr(exc, 'args', [''])[0]}"
            },
        )
