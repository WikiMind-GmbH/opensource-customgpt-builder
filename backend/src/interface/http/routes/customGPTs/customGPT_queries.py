from typing import Annotated
from venv import logger

from fastapi import APIRouter, Depends

from src.bootstrap import DependenciesContainer
from src.contexts.customGPTs.application.ports.cgpt_queries import (
    CgptQueries,
    CustomGPTInfosDTO,
    CustomGPTOverviewDTO,
)
from src.interface.http.composition import dependencies_container
from src.interface.http.mappers_data_and_exceptions.customGPTs.cgpt_queries_classes_and_exceptions import (
    CustomGPTInfosMapper,
    CustomGPTOverviewsMapper,
)
from src.interface.http.schemas.customGPTs.customGPT_queries import (
    CustomGPTInfosSchema,
    CustomGPTOverviewSchema,
)
from src.runtime.logging import LoggerContext, get_logger

logger = get_logger(context=LoggerContext.CUSTOMGPTS, component="QueryRouter")

dependencies_container: DependenciesContainer = dependencies_container

customgpt_queries_router = APIRouter(prefix="/customgpts", tags=["customGPTs: Queries"])


@customgpt_queries_router.get(
    "/retreive-all-custom-gpts",
    operation_id="retreiveAllCustomGpts",
)
def retreive_all_custom_gpts(
    cgpt_queries_adapter: Annotated[
        CgptQueries, Depends(dependencies_container.cgpt_queries_adapter_factory)
    ],
) -> list[CustomGPTOverviewSchema]:
    overviews_dto: list[CustomGPTOverviewDTO] = (
        cgpt_queries_adapter.get_custom_gpt_overviews_ordered_by_created_at()
    )
    overviews_schema: list[CustomGPTOverviewSchema] = CustomGPTOverviewsMapper(
        overviews_dto
    )
    return overviews_schema


@customgpt_queries_router.get(
    "/get-custom-gpt-infos",
    operation_id="getCustomGptInfos",
)
def get_custom_gpt_by_id(
    custom_gpt_id: str,
    cgpt_queries_adapter: Annotated[
        CgptQueries, Depends(dependencies_container.cgpt_queries_adapter_factory)
    ],
) -> CustomGPTInfosSchema:
    logger.debug(msg=f"get-custom-gpt-infos called with id: `{custom_gpt_id}`")
    cgpt_dto: CustomGPTInfosDTO = cgpt_queries_adapter.get_custom_gpt_infos(
        cgpt_id=custom_gpt_id
    )
    return CustomGPTInfosMapper(dto=cgpt_dto)
