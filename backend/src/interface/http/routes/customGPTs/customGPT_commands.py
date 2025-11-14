from fastapi import APIRouter, Depends
from src.interface.http.schemas.customGPTs.customGPT_commands import (
    CustomGptToCreate,
    CustomGptToEdit,
)
from src.bootstrap import DependenciesContainer
from src.interface.http.schemas.common_command import CommandResult
from src.interface.http.deps import deps
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.application.service_functions import (
    create_custom_gpt_service,
    delete_custom_gpt_service,
    edit_custom_gpt_service,
)

deps: DependenciesContainer = deps

customgpt_commands_router = APIRouter(
    prefix="/customgpts", tags=["customGPTs: Commands"]
)


@customgpt_commands_router.delete(
    "/delete-custom-gpt",
    response_model=CommandResult,
    operation_id="deleteCustomGpt",
)
async def delete_custom_gpt_endpoint(
    gpt_id: str,
    uow: CgptUOW = Depends(deps.cgpt_uow_factory),
) -> CommandResult:
    delete_custom_gpt_service(uow, gpt_id)
    return CommandResult(resource_id=gpt_id, message="Succesfully deleted")


# WIP
@customgpt_commands_router.post(
    "/create-custom-gpt",
    response_model=CommandResult,
    operation_id="createCustomGpt",
)
async def create_custom_gpt(
    custom_gpt_infos: CustomGptToCreate,
    uow: CgptUOW = Depends(deps.cgpt_uow_factory),
) -> CommandResult:
    cgpt_id: str = create_custom_gpt_service(
        name=custom_gpt_infos.custom_gpt_name,
        instructions=custom_gpt_infos.custom_gpt_instructions,
        description=custom_gpt_infos.custom_gpt_description,
        uow=uow,
    )
    return CommandResult(
        resource_id=cgpt_id,
        message=f"Custom GPT was succesfully created with id {cgpt_id}",
    )


@customgpt_commands_router.post(
    "/edit-custom-gpt",
    response_model=CommandResult,
    operation_id="editCustomGpt",
)
async def edit_custom_gpt(
    custom_gpt_infos: CustomGptToEdit,
    uow: CgptUOW = Depends(deps.cgpt_uow_factory),
) -> CommandResult:
    edit_custom_gpt_service(
        id=custom_gpt_infos.custom_gpt_id,
        name=custom_gpt_infos.custom_gpt_name,
        instructions=custom_gpt_infos.custom_gpt_instructions,
        description=custom_gpt_infos.custom_gpt_description,
        uow=uow,
    )
    return CommandResult(
        resource_id=custom_gpt_infos.custom_gpt_id,
        message=f"Custom GPT with id {custom_gpt_infos.custom_gpt_id} was succesfully modified",
    )
