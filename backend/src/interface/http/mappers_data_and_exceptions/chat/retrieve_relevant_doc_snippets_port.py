from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    UserHasNoPermissionForCgptOrTheyDontExist,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(
    context=LoggerContext.INTERFACE,
    component="RelevantDocSnippetsPort",
)


def register_exception_handlers_retrieve_relevant_doc_snippets_port(
    app: FastAPI,
) -> None:
    @app.exception_handler(UserHasNoPermissionForCgptOrTheyDontExist)
    async def _permission_denied(_, exc: UserHasNoPermissionForCgptOrTheyDontExist):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.warning("Relevant document snippets access was denied: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "The custom GPT was not found or is not accessible"},
        )
