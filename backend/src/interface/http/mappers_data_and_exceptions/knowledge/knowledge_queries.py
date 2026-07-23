from src.contexts.knowledge.application.ports.knowledge_db_queries import (
    DocumentOverviewDTO,
    DocumentStatusDTO,
    FileCgptAssociationsDTO,
)
from src.interface.http.schemas.knowledge.knowledge_queries import (
    DocumentOverview,
    DocumentStatusSchema,
    FileCgptAssociations,
)


def document_status_dto_to_http_schema(
    dto: DocumentStatusDTO,
) -> DocumentStatusSchema:
    return DocumentStatusSchema(dto.value)


def document_overview_dto_to_http_schema(
    dto: DocumentOverviewDTO,
) -> DocumentOverview:
    return DocumentOverview(
        document_id=dto.document_id,
        name=dto.name,
        file_type=dto.file_type,
        status=document_status_dto_to_http_schema(dto.status),
    )


def file_associations_dto_to_http_schema(
    dto: FileCgptAssociationsDTO,
) -> FileCgptAssociations:
    return FileCgptAssociations(file_id=dto.file_id, cgpt_ids=dto.cgpt_ids)
