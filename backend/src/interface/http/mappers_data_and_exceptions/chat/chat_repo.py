from fastapi.responses import JSONResponse
from src.contexts.chat.application.ports.chat_repo import TemporaryConvRepoError, ConversationNotFoundError


from fastapi import FastAPI, status


def register_query_exception_handlers_chat_repo_port(app: FastAPI) -> None:
    @app.exception_handler(TemporaryConvRepoError)
    async def _tbd(_, exc: TemporaryConvRepoError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unspecified error happened when retreiving chat data"
            },
        )

    @app.exception_handler(ConversationNotFoundError)
    async def not_found(_, exc: ConversationNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Conversation was not found{getattr(exc, 'args', [''])[0]}"},
        )