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
from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    RelevantDocSnippetRetreiverPort,
)
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.domain.models import Conversation, Message
from src.contexts.shared.typing_aliases import Factory


def create_conversation(
    conv_uow_factory: Factory[ConversationUOW], cgpt_id: str | None = None
) -> str:
    with conv_uow_factory() as uow:
        conv: Conversation = uow.conversation_repo.create_conversation(cgpt_id=cgpt_id)
        uow.commit()
        return conv.id


def continue_conversation(
    user_message: str,
    conv_id: str,
    conv_uow_factory: Factory[ConversationUOW],
    cgpt_retreiver: CustomGPTInstructionsRetreiver,
    llm_adapter: LlmPort,
    retrieve_doc_snippets: RelevantDocSnippetRetreiverPort,
    use_rag: bool = False,
) -> str:
    temporary_retriever_results_message: Message | None = None
    small_context_to_query_retriever_with: str | None = None
    big_context_to_query_retriever_with: str | None = None

    with conv_uow_factory() as uow:
        conv: Conversation = uow.conversation_repo.get(conv_id)
        conv.add_user_text_message(user_text_message=user_message)
        uow.commit()  # ToDo: <- no functionality exists to retry llm,

        cgpt_name: str | None = None
        cgpt_instructions: str | None = None

        # this_is_a_chat_with_a_cgpt: bool = conv.customGPT_id is not None
        if conv.customGPT_id is not None:
            cgpt_infos: CustomGPTInfosDTO = cgpt_retreiver.get_cgpt_infos_for_prompt(
                conv.customGPT_id
            )
            cgpt_name = cgpt_infos.name
            cgpt_instructions = cgpt_infos.instructions

        if conv.customGPT_id is not None and use_rag:
            (
                small_context_to_query_retriever_with,
                big_context_to_query_retriever_with,
            ) = conv.create_small_and_bigger_context_text_to_query_retriever_with(
                cgpt_instructions=cgpt_instructions
            )
    # we need to keep this io heavy task out of an open session connection
    if conv.customGPT_id is not None and use_rag:
        if (
            small_context_to_query_retriever_with is None
            or big_context_to_query_retriever_with is None
        ):
            raise RuntimeError(
                "This should be impossible to reach if code wasn't changed to be faulty"
            )
        retrieved_snippets_small_context = retrieve_doc_snippets.retrieve_doc_snippets(
            query_text=small_context_to_query_retriever_with,
            cgpt_id=conv.customGPT_id,
        )
        retrieved_snippets_big_context = retrieve_doc_snippets.retrieve_doc_snippets(
            query_text=big_context_to_query_retriever_with,
            cgpt_id=conv.customGPT_id,
        )
        temporary_retriever_results_message = (
            Conversation.build_temporary_retriever_snippets_message(
                retrieved_snippets_small_context=retrieved_snippets_small_context,
                retrieved_snippets_big_context=retrieved_snippets_big_context,
            )
        )

    messages: list[Message] = conv.create_prompt(
        cgpt_name=cgpt_name, cgpt_instructions=cgpt_instructions
    )
    if temporary_retriever_results_message is not None:
        messages.append(temporary_retriever_results_message)

    assistant_response: str = llm_adapter.get_assistant_text_response(
        messages_dto=messages_domain_to_messages_llm_port_dto(messages)
    )

    with conv_uow_factory() as uow:
        conv: Conversation = uow.conversation_repo.get(conv_id)
        conv.add_assistant_text_message(assistant_text_response=assistant_response)
        uow.commit()
    return assistant_response
