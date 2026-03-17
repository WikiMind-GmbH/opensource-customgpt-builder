from src.contexts.chat.application.mappers import (
    messages_domain_to_messages_llm_port_dto,
)
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CustomGPTInfosDTO,
    CustomGPTInstructionsRetreiver,
)
from src.contexts.chat.application.ports.llm_port import (
    LlmPort,
)
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.domain.models import Conversation, Message


def create_conversation(conv_uow: ConversationUOW, cgpt_id: str | None = None) -> str:
    with conv_uow as uow:
        conv: Conversation = uow.conversation_repo.create_conversation(cgpt_id=cgpt_id)
        uow.commit()
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
        # uow.commit() <- no functionality exists to retry llm, so makes no sense to keep user msg

        cgpt_name: str | None = None
        cgpt_instructions: str | None = None
        if conv.customGPT_id is not None:
            cgpt_infos: CustomGPTInfosDTO = cgpt_retreiver.get_cgpt_infos_for_prompt(
                conv.customGPT_id
            )
            cgpt_name = cgpt_infos.name
            cgpt_instructions = cgpt_infos.instructions

        messages: list[Message] = conv.create_prompt(
            cgpt_name=cgpt_name, cgpt_instructions=cgpt_instructions
        )

        assistant_response: str = llm_adapter.get_assistant_text_response(
            messages_dto=messages_domain_to_messages_llm_port_dto(messages)
        )
        conv.add_assistant_text_message(assistant_text_response=assistant_response)
        uow.commit()
        return assistant_response
