from fastapi import APIRouter, Depends
from src.interface.http.schemas.chat.chat_commands import AssistantMessage, SimplifiedMessage, Role
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import LlmPort
from src.bootstrap import DependenciesContainer
from src.interface.http.schemas.chat.chat_commands import (
    NewChatRequest,
    UserMessageRequest,
)
from src.interface.http.deps import deps


from src.contexts.chat.application.service_functions import (
    continue_conversation,
    create_conversation,
)
from src.contexts.chat.application.ports.uow import ConversationUOW

chat_commands_router = APIRouter(prefix="/chat", tags=["Chat: Commands"])

deps: DependenciesContainer = deps


@chat_commands_router.post(
    "/send-user-message",
    response_model=AssistantMessage,
    operation_id="sendUserMessage",
)
async def send_user_message(
    request: UserMessageRequest,
    conv_uow: ConversationUOW = Depends(deps.conversation_uow_factory),
    llm_adapter: LlmPort = Depends(deps.llm_adapter_factory),
    cgpt_retreiver: CustomGPTInstructionsRetreiver = Depends(
        deps.cgpt_instructions_adapter_factory
    ),
) -> AssistantMessage:
    if isinstance(request, NewChatRequest):
        conversation_id: str = create_conversation(
            conv_uow=conv_uow
        )
    else:
        conversation_id: str = request.conversation_id

    response: str = continue_conversation(
        user_message = request.request_message,
        conv_id=conversation_id,
        conv_uow=conv_uow,
        cgpt_retreiver=cgpt_retreiver,
        llm_adapter=llm_adapter,
    )

    return AssistantMessage(
        conversation_id=conversation_id,
        response_message=SimplifiedMessage(role=Role.assistant, message=response),
    )
