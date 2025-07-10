from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import debugpy

from services.chat_history import retrieve_chat_history_by_id
from services.custom_gpt_service import (
    get_all_custom_gpts,
    send_custom_gpt_info,
)

# from services.chatbot_service import generate_chatbot_response
from schemas.common import (
    ChatHistory,
    CreateCustomGPTResponse,
    CustomGPTInfos,
    ExistingCustomGPT,
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


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post(
    "/chat_history_by_id",
    tags=["chatHistory"],
    summary="Fetches the history of a particular chat id. Identifier = 5",
    response_description="retrives the list of messages and Model ID (0: ChatGPT40, -1: Error, 1/custom_gpt_id: CustomGPTName)",
    response_model=ChatHistory,
    operation_id="getChatHistoryByID",
)
async def get_chat_history(chat_id: int) -> ChatHistory:
    response = await retrieve_chat_history_by_id(chat_id)
    return response


# @app.get("/chat_summary",
#          tags=["chatSummary"],
#          summary="One Liner summary of all chats in the List.  Identifier = 4",
#          response_description="List of chats summary in one line with a Chat_id",
#          response_model=ChatSummary

#          )
# async def get_chats_one_liner() -> ChatSummary:
#     response = get_chat_summaries()
#     return {"one_liners": "text containing one liner of existing chats"}


# @app.get("/get_model_name")
# async def get_model_name(model_name: ModelName):
#     return {"model_name": model_name.base_model_name}


# @app.post("/send_user_message", response_model=AssistantMessage)
# async def send_user_message(request: UserMessageRequest) -> AssistantMessage:

#     response = await generate_chatbot_response(request)
#     return response


# Retrieve All Custom GPTs (List)
@app.get("/display-all-custom-gpts",
         tags=["customGPT"],
         summary="Dispalys all the custom GPTs created",
         response_description="Returns a list of custom gpts created"
         )
async def display_all_custom_gpts() -> list[ExistingCustomGPT]:
    custom_gpt_names_list = await get_all_custom_gpts()
    return custom_gpt_names_list


# # custom gpt by id
# @app.get("/retrieve_custom_gpt_by_id", response_model=ExistingCustomGPT)
# async def read_custom_gpt_by_id(id: int):
#     custom_gpt_info = get_custom_gpt_by_id(id)
#     return custom_gpt_info


# # edit custom gpt
# @app.post("/edit_custom_gpt", response_model=StatusOfStandardResponse)
# async def edit_custom_gpt(edited_information: ExistingCustomGPT):
#     edit_custom_gpt_status = update_custom_gpt(edited_information=edited_information)
#     return edit_custom_gpt_status


# create custom gpt
@app.post(
    "/create_custom_gpt",
    tags=["customGPT"],
    summary="Takes the input from user to create a custom gpt (Name, instruction)",
    response_description="Responds the status of custom gpt created successfully(true) or failure(false) with custom_gpt_id",
    response_model=CreateCustomGPTResponse,
)
async def create_custom_gpt(
    custom_gpt_infos: CustomGPTInfos,
) -> CreateCustomGPTResponse:
    created_gpt_status = await send_custom_gpt_info(custom_gpt_infos=custom_gpt_infos)
    return created_gpt_status
