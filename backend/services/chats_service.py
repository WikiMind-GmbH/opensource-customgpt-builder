from schemas.common import ChatHistory, ChatSummary, Role, SimplifiedMessage


async def retrieve_chat_history_by_id(chat_id: int) -> ChatHistory:
    """Retreives the history of chat messages for a particular chat_id

    Args:
        chat_id (int): id of a selected chat from the chat list

    Returns:
        ChatHistory: Returns Model ID and list of Messages 
    """
    print("id =", chat_id)
    response = 200
    chat_history_list = ChatHistory(
        custom_gpt_id= 0,
        messages=[
            SimplifiedMessage(role=Role.user, message="Hello"),
            SimplifiedMessage(role=Role.assistant, message="Hi, how can I help you?")
        ]
    )
    
    if response == 200:
        return chat_history_list
    else:
        return ChatHistory(custom_gpt_id= -1 , messages= [])
    
    
async def retrieve_chat_summaries_list()-> list[ChatSummary]:
    """Retrieves the list of chat summaries in one liner

    Returns:
        list[ChatSummary]: Returns Chat summaries with chat_id
    """
    response = 200
    chat_summary = [ChatSummary(chat_id=1, chat_summary="summary1"),
                    ChatSummary(chat_id=2, chat_summary="summary2"),
                    ChatSummary(chat_id=3, chat_summary="summary3")]
    if response == 200: 
        return chat_summary
    else:
        return []
