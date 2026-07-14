from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.knowledge.application.ports.knowledge_db_queries import NotFoundError
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="KnowledgeDBQueriesPort")


def register_exception_handlers_knowledge_db_queries_port(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(_, exc: NotFoundError):  # pyright: ignore [reportUnusedFunction] ; REASON: function is used by the decorator
        logger.info("Knowledge database query found no matching document: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )
