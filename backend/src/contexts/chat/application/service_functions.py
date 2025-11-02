from src.contexts.chat.application.mappers import (
    message_domain_to_message_llm_port_dto,
    message_dto_cgpt_retreiver_to_message_domain,
)
from src.contexts.chat.application.ports.llm_port import (
    LlmPort,
    MessageDTOllm,
)
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInstructionsRetreiver,
    MessageDTORetreiver,
)
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.domain.models import (
    Conversation
)


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
    user_message: str,
    conv_id: str,
    conv_uow: ConversationUOW,
    cgpt_retreiver: CustomGPTInstructionsRetreiver,
    llm_adapter: LlmPort,
    use_rag: bool = False,
) -> str:
    with conv_uow as uow:
        conv: Conversation = uow.conversation_repo.get(conv_id)
        conv.add_user_text_message(user_text_message=user_message)
        uow.commit()

        cgpt_id: str | None = conv.customGPT_id
        cgpt_sys_prompt_dto: list[MessageDTORetreiver] = (
            cgpt_retreiver.get_cgpt_sys_prompt(cgpt_id=cgpt_id)
            if cgpt_id is not None
            else []
        )
        cgpt_sys_prompt: list[MessageDTOllm] = [
            message_domain_to_message_llm_port_dto(
                message_dto_cgpt_retreiver_to_message_domain(msg)
            )
            for msg in cgpt_sys_prompt_dto
        ]

        messages_excluding_sys_prompt: list[MessageDTOllm] = [
            message_domain_to_message_llm_port_dto(msg)
            for msg in conv.messages_excl_sysPrompt
        ]

        assistant_response: str = llm_adapter.get_assistant_text_response(
            messages_excluding_sys_prompt=messages_excluding_sys_prompt,
            cgpt_systemprompt=cgpt_sys_prompt,
        )
        conv.add_assistant_text_message(assistant_text_response=assistant_response)
        uow.commit()
        return assistant_response
