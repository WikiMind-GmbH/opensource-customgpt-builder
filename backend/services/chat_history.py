from schemas.common import ChatHistory, ModelInfo, RetreiveChatHistory, Role, SimplifiedMessage


async def retrieve_chat_history_by_id(info: RetreiveChatHistory) -> ChatHistory:
    print("id =", info.chat_id)
    response = 200
    chat_history_list = ChatHistory(
        model_info=ModelInfo(model_id=1, base_model_name="ChatGPT4o", custom_gpt_name=None),
        messages=[
            SimplifiedMessage(role=Role.user, message="Hello"),
            SimplifiedMessage(role=Role.assistant, message="Hi, how can I help you?")
        ]
    )
    
    if response == 200:
        return chat_history_list
    else:
        default_model_info = ModelInfo(model_id=-1, base_model_name="unknown", custom_gpt_name=None)
        return ChatHistory(model_info= default_model_info , messages= [])