from typing import Annotated

from fastapi import APIRouter, Depends

from src.bootstrap import DependenciesContainer
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import LlmPort
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.application.service_functions import (
    continue_conversation,
    create_conversation,
)
from src.interface.http.composition import dependencies_container
from src.interface.http.schemas.chat.chat_commands import (
    AssistantMessage,
    NewChatRequest,
    RoleCmd,
    SimplifiedMessageCmd,
    UserMessageRequest,
)

chat_commands_router = APIRouter(prefix="/chat", tags=["Chat: Commands"])

dependencies_container: DependenciesContainer = dependencies_container


@chat_commands_router.post(
    "/send-user-message",
    operation_id="sendUserMessage",
)
async def send_user_message(
    request: UserMessageRequest,
    conv_uow: Annotated[
        ConversationUOW, Depends(dependencies_container.conversation_uow_factory)
    ],
    llm_adapter: Annotated[
        LlmPort, Depends(dependencies_container.llm_adapter_factory)
    ],
    cgpt_retreiver: Annotated[
        CustomGPTInstructionsRetreiver,
        Depends(dependencies_container.cgpt_retreiver_adapter_factory),
    ],
) -> AssistantMessage:
    if isinstance(request, NewChatRequest):
        conversation_id: str = create_conversation(
            conv_uow=conv_uow, cgpt_id=request.custom_gpt_id
        )
    else:
        conversation_id: str = request.conversation_id

    response: str = continue_conversation(
        user_message=request.request_message,
        conv_id=conversation_id,
        conv_uow=conv_uow,
        cgpt_retreiver=cgpt_retreiver,
        llm_adapter=llm_adapter,
    )

    return AssistantMessage(
        conversation_id=conversation_id,
        response_message=SimplifiedMessageCmd(role=RoleCmd.assistant, message=response),
    )
