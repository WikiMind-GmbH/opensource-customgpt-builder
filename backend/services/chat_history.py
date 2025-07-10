from schemas.common import ChatHistory, Role, SimplifiedMessage


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
    
    