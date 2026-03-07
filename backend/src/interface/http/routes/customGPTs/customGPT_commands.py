from typing import Annotated

from fastapi import APIRouter, Depends

from src.bootstrap import DependenciesContainer
from src.contexts.customGPTs.application.ports.conversation_port import ConversationPort
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from src.contexts.customGPTs.application.service_functions import (
    create_custom_gpt_service,
    delete_custom_gpt_service,
    edit_custom_gpt_service,
)
from src.interface.http.composition import dependencies_container
from src.interface.http.schemas.common_command import CommandResult
from src.interface.http.schemas.customGPTs.customGPT_commands import (
    CustomGptToCreate,
    CustomGptToEdit,
)

dependencies_container: DependenciesContainer = dependencies_container

customgpt_commands_router = APIRouter(
    prefix="/customgpts", tags=["customGPTs: Commands"]
)


@customgpt_commands_router.delete(
    "/delete-custom-gpt",
    operation_id="deleteCustomGpt",
)
def delete_custom_gpt_endpoint(
    gpt_id: str,
    uow: Annotated[CgptUOW, Depends(dependencies_container.cgpt_uow_factory)],
    conv_adapter: Annotated[
        ConversationPort, Depends(dependencies_container.conversation_adapter_factory)
    ],
) -> CommandResult:
    delete_custom_gpt_service(uow, gpt_id, conv_adapter)
    return CommandResult(resource_id=gpt_id, message="Succesfully deleted")


# WIP
@customgpt_commands_router.post(
    "/create-custom-gpt",
    operation_id="createCustomGpt",
)
def create_custom_gpt(
    custom_gpt_infos: CustomGptToCreate,
    uow: Annotated[CgptUOW, Depends(dependencies_container.cgpt_uow_factory)],
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
    operation_id="editCustomGpt",
)
def edit_custom_gpt(
    custom_gpt_infos: CustomGptToEdit,
    uow: Annotated[CgptUOW, Depends(dependencies_container.cgpt_uow_factory)],
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
