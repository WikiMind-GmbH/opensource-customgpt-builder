from fastapi import APIRouter, Depends
from src.bootstrap import DependenciesContainer
from src.contexts.customGPTs.application.ports.cgpt_queries import CgptQueries, CustomGPTInfosDTO
from src.interface.http.mappers_data_and_exceptions.chat.cgpt_queries_classes_and_exceptions import CustomGPTInfosMapper, CustomGPTOverviewsMapper
from src.interface.http.schemas.customGPTs.customGPT_queries import CustomGPTInfosSchema, CustomGPTOverviewSchema
from src.contexts.customGPTs.application.ports.cgpt_queries import CustomGPTOverviewDTO
from src.interface.http.deps import deps
from sqlalchemy.orm import Session

deps: DependenciesContainer = deps

customgpt_queries_router = APIRouter(prefix="/customgpts", tags=["customGPTs: Queries"])

@customgpt_queries_router.get(
    "/retreive-all-custom-gpts",
    response_model=list[CustomGPTOverviewSchema],
    operation_id="retreiveAllCustomGpts",
)
async def retreive_all_custom_gpts(
    cgpt_queries_adapter: CgptQueries = Depends(deps.cgpt_queries_adapter_factory),
) -> list[CustomGPTOverviewSchema]:
    overviews_dto:list[CustomGPTOverviewDTO] = cgpt_queries_adapter.get_custom_gpt_overviews_ordered_by_created_at()
    overviews_schema:list[CustomGPTOverviewSchema] = CustomGPTOverviewsMapper(overviews_dto)
    return overviews_schema

@customgpt_queries_router.get(
    "/get-custom-gpt-infos",
    response_model=CustomGPTInfosSchema,
    operation_id="getCustomGptInfos",
)
async def get_custom_gpt_by_id(
    custom_gpt_id: str,
    cgpt_queries_adapter: CgptQueries = Depends(deps.cgpt_queries_adapter_factory),
) -> CustomGPTInfosSchema:
    cgpt_dto: CustomGPTInfosDTO = cgpt_queries_adapter.get_custom_gpt_infos(cgpt_id=custom_gpt_id)
    return CustomGPTInfosMapper(dto= cgpt_dto)
