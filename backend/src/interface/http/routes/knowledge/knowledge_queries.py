from fastapi import APIRouter

from src.bootstrap import DependenciesContainer
from src.interface.http.composition import dependencies_container

dependencies_container: DependenciesContainer = dependencies_container

customgpt_queries_router = APIRouter(prefix="/customgpts", tags=["customGPTs: Queries"])


# @customgpt_queries_router.get(
#     "/retreive-all-custom-gpts",
#     operation_id="retreiveAllCustomGpts",
# )
# def retreive_all_custom_gpts(
#     cgpt_queries_adapter: Annotated[
#         CgptQueries, Depends(dependencies_container.cgpt_queries_adapter_factory)
#     ],
# ) -> list[CustomGPTOverviewSchema]:
#     overviews_dto: list[CustomGPTOverviewDTO] = (
#         cgpt_queries_adapter.get_custom_gpt_overviews_ordered_by_created_at()
#     )
#     overviews_schema: list[CustomGPTOverviewSchema] = CustomGPTOverviewsMapper(
#         overviews_dto
#     )
#     return overviews_schema


# @customgpt_queries_router.get(
#     "/get-custom-gpt-infos",
#     operation_id="getCustomGptInfos",
# )
# def get_custom_gpt_by_id(
#     custom_gpt_id: str,
#     cgpt_queries_adapter: Annotated[
#         CgptQueries, Depends(dependencies_container.cgpt_queries_adapter_factory)
#     ],
# ) -> CustomGPTInfosSchema:
#     cgpt_dto: CustomGPTInfosDTO = cgpt_queries_adapter.get_custom_gpt_infos(
#         cgpt_id=custom_gpt_id
#     )
#     return CustomGPTInfosMapper(dto=cgpt_dto)
