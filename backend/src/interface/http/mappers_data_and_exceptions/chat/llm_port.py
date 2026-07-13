from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.llm_port import (
    ErrorWhileCallingAPI,
    NoAssistantResponse,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="LlmPort")


def register_exception_handlers_llm_port(app: FastAPI) -> None:
    @app.exception_handler(NoAssistantResponse)
    async def _not_found(_, exc: NoAssistantResponse):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.error("LLM returned no assistant response", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "Service temporarily unavailable"},
        )

    @app.exception_handler(ErrorWhileCallingAPI)
    async def _tbd(_, exc: ErrorWhileCallingAPI):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.error("LLM provider call failed", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "Service temporarily unavailable"},
        )
