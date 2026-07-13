from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.domain.models import Conversation
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="ChatDomain")


def register_exception_handlers_chat_domain(
    app: FastAPI,
) -> None:
    @app.exception_handler(Conversation.CantUseRagIfNoCgptIsPassedError)
    async def _not_found(_, exc: Conversation.CantUseRagIfNoCgptIsPassedError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.info(
            "RAG request rejected because the conversation has no custom GPT: %s", exc
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": "RAG requires a custom GPT"},
        )
