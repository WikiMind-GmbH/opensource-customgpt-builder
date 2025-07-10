from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import debugpy
from services.chatbot_service import send_user_message_helper
from services.chats_service import (
    get_chat_history_helper,
    get_chat_summaries_helper,
)
from services.custom_gpt_service import (
    delete_custom_gpt_helper,
    retreive_all_custom_gpts_helper,
    get_custom_gpt_by_id_helper,
    create_or_custom_gpt_helper,
)

# from services.chatbot_service import generate_chatbot_response
from schemas.common import (
    AssistantMessage,
    ChatHistory,
    ChatSummary,
    CreateOrEditCustomGPTStatus,
    CustomGptToCreateOrEdit,
    DeleteCustomGPTStatus,
    ExistingCustomGPT,
    UserMessageRequest,
)

app = FastAPI(
    root_path="/api",  # Explanation: While the proxy strips the /api prefix, we stil need this here: https://fastapi.tiangolo.com/advanced/behind-a-proxy/#proxy-with-a-stripped-path-prefix
)

origins = [
    f"https://localhost",
]

# Add the CORSMiddleware to your application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from these origins
    allow_credentials=True,  # Allows cookies, authorization headers, etc.
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Retrives the history of a chat by ID
@app.post(
    "/chat-history-by-id",
    tags=["Chat"],
    summary="Fetches the history of a particular chat id. Identifier = 5",
    response_description="retrives the list of messages and Model ID (0: ChatGPT40, -1: Error, 1/custom_gpt_id: CustomGPTName)",
    response_model=ChatHistory,
    operation_id="getChatHistoryByID",
)
async def get_chat_history(chat_id: int) -> ChatHistory:
    response = await get_chat_history_helper(chat_id)
    return response


# Retrieves the list of Chat Summaries
@app.get(
    "/get-chat-summaries",
    tags=["Chat"],
    summary="One Liner summary of all chats in the Chat List.  Identifier = 3",
    response_description="List of chats summary in one line with a Chat ID",
    response_model=list[ChatSummary],
    operation_id="getChatSummaries",
)
async def get_chat_summaries() -> list[ChatSummary]:
    response = await get_chat_summaries_helper()
    return response


# Send the User Message to the GPT Model
@app.post(
    "/send-user-message",
    tags=["Chat"],
    summary="Process the user chat message and send response back from the Model selected, Indentifier = 8",
    response_description="Generates the response from the assistant with a conversation ID",
    response_model=AssistantMessage,
    operation_id="sendUserMessage",
)
async def send_user_message(request: UserMessageRequest) -> AssistantMessage:
    response = await send_user_message_helper(request)
    return response


# Retrieve All Custom GPTs (List)
@app.get(
    "/retreive-all-custom-gpts",
    tags=["customGPTs"],
    summary="Dispalys all the custom GPTs created, Indentfier = 4",
    response_description="Returns a list of custom gpts created",
    response_model=list[ExistingCustomGPT],
    operation_id="retreiveAllCustomGPTs",
)
async def retreive_all_custom_gpts() -> list[ExistingCustomGPT]:
    custom_gpt_names_list = await retreive_all_custom_gpts_helper()
    return custom_gpt_names_list


# Retrieve a custom gpt by ID
@app.get(
    "/get-custom-gpt-infos",
    tags=["customGPTs"],
    summary="User chats with Custom GPT, indetifier = 13",
    response_description="Information of Custom GPT so as to the Navigate to its Chat Page",
    response_model=ExistingCustomGPT,
    operation_id="getCustomGPTInfos",
)
async def get_custom_gpt_by_id(custom_gpt_id: int):
    custom_gpt_info = await get_custom_gpt_by_id_helper(custom_gpt_id)
    return custom_gpt_info

# Deletes the Custom GPT By ID
@app.delete(
    "/delete-custom-gpt",
    tags=["customGPTs"],
    summary="delete the existing custom GPT by ID, identifier = 15",
    response_description="Send the status of deleted successfully(true) or failure(false)",
    operation_id="deleteCustomGPT",
)
async def delete_custom_gpt(custom_gpt_id: int) -> DeleteCustomGPTStatus:
    response_deletion = await delete_custom_gpt_helper(custom_gpt_id=custom_gpt_id)
    return response_deletion


# Create a New Custom GPT
@app.post(
    "/create-or-edit-custom-gpt",
    tags=["customGPTs"],
    summary="Takes the input from user to create a custom gpt (Name, instruction), Indentfier = 11/ create",
    response_description="Responds the status of custom gpt created successfully(true) or failed(false) with custom_gpt_id",
    response_model=CreateOrEditCustomGPTStatus,
    operation_id="createOrEditCustomGPT",
)
async def create_or_custom_gpt(
    custom_gpt_infos: CustomGptToCreateOrEdit,
) -> CreateOrEditCustomGPTStatus:
    created_gpt_status = await create_or_custom_gpt_helper(custom_gpt_infos=custom_gpt_infos)
    return created_gpt_status
