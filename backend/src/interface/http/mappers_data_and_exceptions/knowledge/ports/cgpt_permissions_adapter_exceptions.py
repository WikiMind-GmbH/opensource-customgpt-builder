from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    UserHasNoPermissionForCgptOrTheyDontExist,
)


def register_query_exception_handlers_cgpt_permission_port(app: FastAPI) -> None:
    @app.exception_handler(UserHasNoPermissionForCgptOrTheyDontExist)
    async def _not_found(_, exc: UserHasNoPermissionForCgptOrTheyDontExist):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Cgpts not found: {getattr(exc, 'args', [''])[0]}"},
        )
