from typing import Annotated

from fastapi import APIRouter, Depends

from src.bootstrap import DependenciesContainer
from src.composition import dependencies_container
from src.contexts.chat.application.orchestration import (
    continue_conversation,
    create_conversation,
)
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import LlmPort
from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    RelevantDocSnippetRetreiverPort,
)
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.shared.typing_aliases import Factory
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
def send_user_message(
    request: UserMessageRequest,
    conv_uow_factory: Annotated[
        Factory[ConversationUOW],
        Depends(dependencies_container.conversation_uow_factory_factory),
    ],
    llm_adapter: Annotated[
        LlmPort, Depends(dependencies_container.llm_adapter_factory)
    ],
    cgpt_retreiver: Annotated[
        CustomGPTInstructionsRetreiver,
        Depends(dependencies_container.cgpt_retreiver_adapter_factory),
    ],
    retrieve_doc_snippets: Annotated[
        RelevantDocSnippetRetreiverPort,
        Depends(dependencies_container.retrieve_doc_snippets_adapter_factory),
    ],
) -> AssistantMessage:
    if isinstance(request, NewChatRequest):
        conversation_id: str = create_conversation(
            conv_uow_factory=conv_uow_factory, cgpt_id=request.custom_gpt_id
        )
    else:
        conversation_id: str = request.conversation_id

    response: str = continue_conversation(
        user_message=request.request_message,
        conv_id=conversation_id,
        conv_uow_factory=conv_uow_factory,
        cgpt_retreiver=cgpt_retreiver,
        llm_adapter=llm_adapter,
        retrieve_doc_snippets=retrieve_doc_snippets,
        use_rag=request.use_rag,
    )

    return AssistantMessage(
        conversation_id=conversation_id,
        response_message=SimplifiedMessageCmd(role=RoleCmd.assistant, message=response),
    )
