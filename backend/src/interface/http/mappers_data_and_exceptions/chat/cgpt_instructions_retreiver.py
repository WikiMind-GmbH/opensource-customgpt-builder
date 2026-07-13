from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CgptNotFoundError,
    DefaultCGPTRetreiverError,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(
    context=LoggerContext.INTERFACE,
    component="CustomGPTInstructionsRetrieverPort",
)


def register_exception_handlers_cgpt_instruction_retreiver_port(
    app: FastAPI,
) -> None:
    @app.exception_handler(CgptNotFoundError)
    async def _not_found(_, exc: CgptNotFoundError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.warning("Custom GPT instructions were not found or accessible: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "The custom GPT was not found or is not accessible"},
        )

    @app.exception_handler(DefaultCGPTRetreiverError)
    async def _tbd(_, exc: DefaultCGPTRetreiverError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.error("Custom GPT instructions retrieval failed", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )
