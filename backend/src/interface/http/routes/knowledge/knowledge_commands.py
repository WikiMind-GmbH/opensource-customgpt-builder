from typing import Annotated

from fastapi import APIRouter, Depends

from src.bootstrap import DependenciesContainer
from src.contexts.knowledge.application.orchestration_use_cases.upload_document_use_case import (
    upload_document_complete_workflow_return_file_id,
)
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    CgptPermissionCheckerPort,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingGeneratorPort,
)
from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    ExtractTextFromDocumentPort,
)
from src.contexts.knowledge.application.ports.file_storage_port import RawFileStorePort
from src.contexts.knowledge.application.ports.knowledge_uow import KnowledgeUOW
from src.contexts.knowledge.application.ports.task_scheduler_port import (
    TaskSchedulerPort,
)
from src.contexts.knowledge.application.ports.vector_store_port import (
    VectorStorePortTextChunks,
)
from src.contexts.shared.typing_aliases import Factory
from src.interface.http.composition import dependencies_container
from src.interface.http.schemas.common_command import CommandResult
from src.interface.http.schemas.knowledge.knowledge_commands import (
    UploadFileForKnowledgeContext,
)

dependencies_container: DependenciesContainer = dependencies_container

knowledge_commands_router = APIRouter(prefix="/knowledge", tags=["knowledge: Commands"])


@knowledge_commands_router.delete(
    "/delete-files",
    operation_id="deleteFiles",
)
def delete_files_endpoint(
    file_ids: list[str],
    # uow_metadata db
    # adapter vector db
) -> list[CommandResult]:
    raise NotImplementedError
    # delete_files_service(file_ids)
    # return


# WIP
@knowledge_commands_router.post(
    "/upload-files",
    operation_id="uploadFiles",
)
async def upload_file(
    file: UploadFileForKnowledgeContext,
    extract_text_from_document_adapter: Annotated[
        ExtractTextFromDocumentPort,
        Depends(dependencies_container.extract_text_from_document_adapter_factory),
    ],
    knowledge_uow_factory: Annotated[
        Factory[KnowledgeUOW],
        Depends(dependencies_container.knowledge_uow_factory_factory),
    ],
    cgpt_permissions_adapter: Annotated[
        CgptPermissionCheckerPort,
        Depends(dependencies_container.cgpt_permissions_adapter_factory),
    ],
    file_storage_adapter: Annotated[
        RawFileStorePort,
        Depends(dependencies_container.file_storage_adapter_factory),
    ],
    task_scheduler: Annotated[
        TaskSchedulerPort,
        Depends(dependencies_container.task_scheduler_factory),
    ],
    vector_store_adapter: Annotated[
        VectorStorePortTextChunks,
        Depends(dependencies_container.vector_store_adapter_factory),
    ],
    embedding_generator_adapter: Annotated[
        EmbeddingGeneratorPort,
        Depends(dependencies_container.embedding_generator_adapter_factory),
    ],
) -> CommandResult:
    file_bytes_content = await file.uploadFile.read()

    uuid_of_file = upload_document_complete_workflow_return_file_id(
        file_bytes_content=file_bytes_content,
        file_name_with_ending=file.filename,
        extract_text_from_document_adapter=extract_text_from_document_adapter,
        knowledge_uow_factory=knowledge_uow_factory,
        accessible_to_cgpts=file.gpt_ids,
        cgpt_permissions_adapter=cgpt_permissions_adapter,
        file_storage_adapter=file_storage_adapter,
        task_scheduler=task_scheduler,
        vector_store_adapter=vector_store_adapter,
        embedding_generator_adapter=embedding_generator_adapter,
    )

    return CommandResult(
        resource_id=str(uuid_of_file),
        message="File uploaded successfully.",
    )
