from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    EmptyListToCheckPassedError,
    UserHasNoPermissionForCgptOrTheyDontExist,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="CgptPermissionPort")


def register_exception_handlers_cgpt_permission_port(app: FastAPI) -> None:
    @app.exception_handler(UserHasNoPermissionForCgptOrTheyDontExist)
    async def _not_found(_, exc: UserHasNoPermissionForCgptOrTheyDontExist):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.warning("Custom GPT permission check denied access: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "The custom GPT was not found or is not accessible"},
        )

    @app.exception_handler(EmptyListToCheckPassedError)
    async def _empty_list(_, exc: EmptyListToCheckPassedError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.info("Custom GPT permission check rejected an empty id list")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "At least one custom GPT id must be supplied"},
        )
