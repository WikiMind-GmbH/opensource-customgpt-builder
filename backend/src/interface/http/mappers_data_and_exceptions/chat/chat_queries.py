from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.chat_queries import NotFoundError


def register_query_exception_handlers_queries_port(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(_, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"Conversation not found: {getattr(exc, 'args', [''])[0]}"
            },
        )