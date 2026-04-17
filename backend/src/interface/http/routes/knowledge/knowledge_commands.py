from fastapi import APIRouter

from src.bootstrap import DependenciesContainer
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
    delete_files_service(file_ids)
    return


# WIP
@knowledge_commands_router.post(
    "/upload-files",
    operation_id="uploadFiles",
)
async def upload_files(
    files: list[UploadFileForKnowledgeContext],
) -> CommandResult:
    
