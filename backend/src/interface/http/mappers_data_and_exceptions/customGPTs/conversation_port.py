from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.customGPTs.application.ports.customgpt_repo import CgptNotFound


def register_query_exception_handlers_conv_port(app: FastAPI) -> None:
    @app.exception_handler(CgptNotFound)
    async def _not_found(_, exc: CgptNotFound):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"Conversation not found: {getattr(exc, 'args', [''])[0]}"
            },
        )
