from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.bootstrap import DependenciesContainer
from src.composition import dependencies_container
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
)
from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    DocumentOverviewDTO,
    FileCgptAssociationsDTO,
    KnowledgeDBQueriesPort,
)
from src.interface.http.mappers_data_and_exceptions.knowledge.knowledge_queries import (
    document_overview_dto_to_http_schema,
    document_status_dto_to_http_schema,
    file_associations_dto_to_http_schema,
)
from src.interface.http.schemas.knowledge.knowledge_queries import (
    DocumentOverview,
    DocumentStatusSchema,
    FileCgptAssociations,
)

dependencies_container: DependenciesContainer = dependencies_container

knowledge_queries_router = APIRouter(prefix="/knowledge", tags=["knowledge: Queries"])


@knowledge_queries_router.get(
    "/check_status_of_document",
    operation_id="checkStatusOfDocument",
)
def check_status_of_document(
    cgpt_permissions_adapter: Annotated[
        CgptPermissionCheckerPort,
        Depends(dependencies_container.cgpt_permissions_adapter_factory),
    ],
    knowledge_db_queries_adapter: Annotated[
        KnowledgeDBQueriesPort,
        Depends(dependencies_container.knowledge_db_queries_adapter_factory),
    ],
    document_id: UUID,
    cgpt_id: str,
) -> DocumentStatusSchema:
    cgpt_permissions_adapter.assure_user_has_access_to_cgpts([cgpt_id])
    status_dto = knowledge_db_queries_adapter.check_status_of_document(
        document_id=document_id, cgpt_id=cgpt_id
    )
    return document_status_dto_to_http_schema(status_dto)


@knowledge_queries_router.get(
    "/documents",
    operation_id="getDocumentsForCgpt",
)
def get_documents_for_cgpt(
    cgpt_permissions_adapter: Annotated[
        CgptPermissionCheckerPort,
        Depends(dependencies_container.cgpt_permissions_adapter_factory),
    ],
    knowledge_db_queries_adapter: Annotated[
        KnowledgeDBQueriesPort,
        Depends(dependencies_container.knowledge_db_queries_adapter_factory),
    ],
    cgpt_id: str,
) -> list[DocumentOverview]:
    cgpt_permissions_adapter.assure_user_has_access_to_cgpts([cgpt_id])
    documents: list[DocumentOverviewDTO] = (
        knowledge_db_queries_adapter.get_documents_for_cgpt(cgpt_id)
    )
    return [document_overview_dto_to_http_schema(document) for document in documents]


@knowledge_queries_router.get(
    "/file-associations",
    operation_id="getFileAssociations",
)
def get_all_documents_with_their_linked_cgpts(
    knowledge_db_queries_adapter: Annotated[
        KnowledgeDBQueriesPort,
        Depends(dependencies_container.knowledge_db_queries_adapter_factory),
    ],
) -> list[FileCgptAssociations]:
    associations: list[FileCgptAssociationsDTO] = (
        knowledge_db_queries_adapter.get_file_cgpt_associations()
    )
    return [file_associations_dto_to_http_schema(item) for item in associations]
