from schemas.common import AssistantMessage, SimplifiedMessage, UserMessageRequest, Role


async def generate_chatbot_response(
    user_request: UserMessageRequest,
) -> AssistantMessage:
    """Calls the OpenAI model api using user message as input and generates OpenAI model's response as output

    Args:
        user_request (UserMessageRequest): Chat Message from user with Custom GPT ID

    Returns:
        AssistantMessage: Generated message from Assitant (Openai model) with Conversation ID
    """
    print("The model id: ", user_request.custom_gpt_id)
    print("The user message: ", user_request.request_message)

    response = 200
    if response == 200:

        response_message = SimplifiedMessage(
            role=Role.assistant, message="Response generated from Model"
        )

        assisant_message = AssistantMessage(
            conversation_id=1, response_message=response_message
        )

        return assisant_message
    else:
        response_message_error = SimplifiedMessage(role=Role.assistant, message="")
        return AssistantMessage(
            conversation_id=-1, response_message=response_message_error
        )
