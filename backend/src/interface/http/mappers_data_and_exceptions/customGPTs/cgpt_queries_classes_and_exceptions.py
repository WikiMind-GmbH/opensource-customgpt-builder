from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.customGPTs.application.ports.cgpt_queries import (
    CustomGPTInfosDTO,
    CustomGPTOverviewDTO,
)
from src.contexts.customGPTs.infrastructure.adapters.cgpt_queries import (
    NotFoundError,
    QueryError,
)
from src.interface.http.schemas.customGPTs.customGPT_queries import (
    CustomGPTInfosSchema,
    CustomGPTOverviewSchema,
)


def register_query_exception_handlers_cgpt_query_port(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(_, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"Conversation not found: {getattr(exc, 'args', [''])[0]}"
            },
        )

    @app.exception_handler(QueryError)
    async def _query_error(_, exc: QueryError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "Query failed"},
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
