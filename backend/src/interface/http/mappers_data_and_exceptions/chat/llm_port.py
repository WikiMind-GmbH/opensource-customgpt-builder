from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.llm_port import (
    ErrorWhileCallingAPI,
    NoAssistantResponse,
)


def register_exception_handlers_llm_port(app: FastAPI) -> None:
    @app.exception_handler(NoAssistantResponse)
    async def _not_found(_, exc: NoAssistantResponse):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "API of LLM returned without an assistant response"},
        )

    @app.exception_handler(ErrorWhileCallingAPI)
    async def _tbd(_, exc: ErrorWhileCallingAPI):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "An unspecified error happened when callin the llm API"},
        )
