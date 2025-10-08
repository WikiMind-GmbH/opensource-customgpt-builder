from typing import List, Sequence
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import CustomGPTInstructionsRetreiver
from src.contexts.chat.application.exceptions import ConversationNonExistentError
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.domain.models import Conversation, ConversationFilteredForClient, ConversationOverview, Message, Role, UserOrAssistantTextMessage


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
            conv_filtered_for_client:ConversationFilteredForClient = conv.get_conversation_filtered_for_client()
            return conv_filtered_for_client
    except ConversationNonExistentError:
        raise ConversationNonExistentError
    except Exception:
        raise Exception

def process_sent_user_message(user_msg:str, conv_uow:ConversationUOW, cgpt_retreiver:CustomGPTInstructionsRetreiver, conv_id: str | None = None,  custom_gpt_id: str| None = None, use_rag:bool = False):
         
    def get_or_create_conversation(uow: ConversationUOW, cgpt_retreiver:CustomGPTInstructionsRetreiver, conv_id: str| None = None,custom_gpt_id: str| None = None )->Conversation:
        this_is_a_new_conversation: bool = conv_id is not None
        if not this_is_a_new_conversation: 
            return uow.conversation_repo.create_conversation(customGptId=custom_gpt_id)
            if custom_gpt_id: 
                add_cgpt_info_to_messages()
        return uow.conversation_repo.get(conv_id)

    
    with conv_uow as uow:
        conv: Conversation = get_or_create_conversation(conv_id,uow)

        
        