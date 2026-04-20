from fastapi import APIRouter

from src.bootstrap import DependenciesContainer
from src.contexts.knowledge.application.ports.cgpt_permissions_port import CgptPermissionCheckerPort
from src.contexts.knowledge.application.ports.knowledge_db_queries import DocumentStatus
from src.interface.http.composition import dependencies_container

dependencies_container: DependenciesContainer = dependencies_container

knowledge_queries_router = APIRouter(prefix="/knowledge", tags=["knowledge: Queries"])

dependencies_container: DependenciesContainer = dependencies_container

@knowledge_queries_router.get(
    "/check_status_of_document",
    opertation_id = "checkStatusOfDocument",
)
def check_status_of_document(
    cgpt_permission_adapter: CgptPermissionCheckerPort,
    cgpt_id: str,
)-> DocumentStatus:
    # check permissions
    
    

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
