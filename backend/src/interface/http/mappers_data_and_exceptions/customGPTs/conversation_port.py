from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.customGPTs.application.ports.customgpt_repo import CgptNotFound
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="CustomGPTRepoPort")


def register_exception_handlers_conv_port(app: FastAPI) -> None:
    @app.exception_handler(CgptNotFound)
    async def _not_found(_, exc: CgptNotFound):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.warning("Custom GPT repository found no accessible resource: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "The custom GPT was not found or is not accessible"},
        )
