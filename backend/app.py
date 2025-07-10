from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.chat_history import retrieve_chat_history_by_id
from services.custom_gpt_service import get_custom_gpt_by_id,  send_custom_gpt_info, update_custom_gpt
from services.chatbot_service import generate_chatbot_response
from schemas.common import (
    AssistantMessage,
    ChatHistory,
    CreateCustomGPTResponse,
    CustomGPTInfos,
    ExistingCustomGPT,
    ModelName,
    RetreiveChatHistory,
    StatusOfStandardResponse,
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


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/chat_history_by_id")
async def get_chat_history(info: RetreiveChatHistory) -> ChatHistory:
    response = await retrieve_chat_history_by_id(info)
    return response

@app.get("/chats_list_by_one_liner")
async def get_chats_one_liner():
    return {"one_liners": "text containing one liner of existing chats"}


@app.get("/get_model_name")
async def get_model_name(model_name: ModelName):
    return {"model_name": model_name.base_model_name}


@app.post("/send_user_message", response_model=AssistantMessage)
async def send_user_message(request: UserMessageRequest) -> AssistantMessage:

    response = await generate_chatbot_response(
     request
    )
    return response


# Retrieve All Custom GPTs (List)
# @app.get("/retrieve_custom_gpts_list", response_model=)
# async def read_custom_gpt_list():
#     custom_gpt_names_list = get_custom_gpts_list()
#     return custom_gpt_names_list


#custom gpt by id
@app.get("/retrieve_custom_gpt_by_id", response_model=ExistingCustomGPT)
async def read_custom_gpt_by_id(id: int):
    custom_gpt_info = get_custom_gpt_by_id(id)
    return custom_gpt_info

#edit custom gpt
@app.post("/edit_custom_gpt", response_model= StatusOfStandardResponse)
async def edit_custom_gpt(edited_information: ExistingCustomGPT):
    edit_custom_gpt_status = update_custom_gpt(edited_information=edited_information)
    return edit_custom_gpt_status

# create custom gpt 
@app.post("/create_custom_gpt")
async def create_custom_gpt(custom_gpt_infos: CustomGPTInfos) -> CreateCustomGPTResponse:
    created_gpt_status = await send_custom_gpt_info(custom_gpt_infos=custom_gpt_infos)
    return created_gpt_status