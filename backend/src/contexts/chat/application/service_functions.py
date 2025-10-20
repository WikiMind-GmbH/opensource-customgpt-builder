from typing import List, Sequence
from src.contexts.chat.application.mappers import message_dto_to_message_domain
from src.contexts.chat.application.ports.llm_port import (
    ErrorWhileCallingAPI,
    LlmPort,
    NoAssistantResponse,
)
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
    MessageDTO,
)
from src.contexts.chat.application.exceptions import ConversationNonExistentError
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.domain.models import (
    Conversation,
    ConversationFilteredForClient,
    ConversationOverview,
    Message,
    Role,
    TextMessage,
)


def get_chat_summaries_service(conv_uow: ConversationUOW) -> List[ConversationOverview]:
    with conv_uow as uow:
        summaries: Sequence[ConversationOverview] = (
            uow.conversation_repo.list_all_overviews_ordered_by_latest_msg()
        )
        return list(summaries)


def retrieve_chat_history_by_id(
    conv_id: str, conv_uow: ConversationUOW
) -> ConversationFilteredForClient:
    try:
        with conv_uow as uow:
            conv: Conversation = uow.conversation_repo.get(conv_id)
            conv_filtered_for_client: ConversationFilteredForClient = (
                conv.get_conversation_filtered_for_client
            )
            return conv_filtered_for_client
    except ConversationNonExistentError:
        raise ConversationNonExistentError
    except Exception:
        raise Exception


def create_conversation(
    custom_gpt_id: str | None,
    conv_uow: ConversationUOW,
) -> str:

    with conv_uow as uow:
        conv: Conversation = uow.conversation_repo.create_conversation(
            cgpt_id=custom_gpt_id
        )
        return conv.id


def continue_conversation(
    conv_id: str,
    conv_uow: ConversationUOW,
    cgpt_retreiver: CustomGPTInstructionsRetreiver,
    llm_adapter: LlmPort,
    use_rag: bool = False,
) -> str:

    try:
        with conv_uow as uow:
            conv: Conversation = uow.conversation_repo.get(conv_id)
            cgpt_id: str | None = conv.customGPT_id
            cgpt_sys_prompt_dto: list[MessageDTO] = (
                cgpt_retreiver.get_cgpt_sys_prompt(cgpt_id=cgpt_id)
                if cgpt_id is not None
                else []
            )
            cgpt_sys_prompt: list[Message] = [message_dto_to_message_domain(msg_dto) for msg_dto in cgpt_sys_prompt_dto]
            assistant_response: str = llm_adapter.get_assistant_response(
                messages_excluding_sys_prompt=conv.messages_excl_sysPrompt,
                cgpt_systemprompt=cgpt_sys_prompt,
            )
            return assistant_response
    except ConversationNonExistentError:
        raise ConversationNonExistentError
    except NoAssistantResponse:
        raise NoAssistantResponse
    except ErrorWhileCallingAPI:
        raise ErrorWhileCallingAPI
    except Exception:
        raise Exception
