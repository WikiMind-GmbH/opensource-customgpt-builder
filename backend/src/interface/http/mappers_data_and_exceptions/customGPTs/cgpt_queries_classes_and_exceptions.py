from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.customGPTs.application.ports.cgpt_queries import (
    CustomGPTInfosDTO,
    CustomGPTOverviewDTO,
)
from src.contexts.customGPTs.infrastructure.adapters.cgpt_queries_adapter import (
    NotFoundError,
    QueryError,
)
from src.interface.http.schemas.customGPTs.customGPT_queries import (
    CustomGPTInfosSchema,
    CustomGPTOverviewSchema,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.INTERFACE, component="CustomGPTQueriesPort")


def register_exception_handlers_cgpt_query_port(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(_, exc: NotFoundError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.warning("Custom GPT query found no accessible resource: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "The custom GPT was not found or is not accessible"},
        )

    @app.exception_handler(QueryError)
    async def _query_error(_, exc: QueryError):  # pyright: ignore [reportUnusedFunction] ; REASON: 'false flag' function is used by the decorator
        logger.error("Custom GPT query failed", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )


def CustomGPTOverviewsMapper(
    dtos: list[CustomGPTOverviewDTO],
) -> list[CustomGPTOverviewSchema]:
    return [
        CustomGPTOverviewSchema(custom_gpt_id=dto.id, custom_gpt_name=dto.name)
        for dto in dtos
    ]


def CustomGPTInfosMapper(dto: CustomGPTInfosDTO) -> CustomGPTInfosSchema:
    return CustomGPTInfosSchema(
        custom_gpt_id=dto.id,
        custom_gpt_name=dto.name,
        custom_gpt_description=dto.description,
        custom_gpt_instructions=dto.instructions,
    )
