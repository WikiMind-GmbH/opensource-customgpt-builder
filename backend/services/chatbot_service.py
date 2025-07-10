from schemas.common import AssistantMessage, UserMessageRequest

async def generate_chatbot_response(user_request: UserMessageRequest) -> AssistantMessage:
    """Calls the OpenAI model api using user message as input and generates openai model's response as output

    Args:
        user_request (UserMessageRequest): Chat Message from user

    Returns:
        AssistantMessage: Generated message from Assitant (Openai model)
    """
    print("The model id: ", user_request.model_id)
    print("The user message: ", user_request.message)

    response = 200

    if response == 200: 

        response_message = "Message generated from gpt"
    
        assisant_message = AssistantMessage(conversation_id=1,
                                            response_message=response_message)
        
        return assisant_message
    else:
        return AssistantMessage(conversation_id=-1,response_message="")