from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from models.models import ConversationDB, CustomGptsDB
from services.database import create_db_and_tables, get_session
from services.chats_service import (
    retrieve_chat_history_by_id,
    retrieve_chat_summaries_list,
    send_user_message_service,
)
from services.custom_gpt_service import (
    get_all_custom_gpts,
    retrieve_custom_gpt_by_id,
    delete_custom_gpt,
    create_or_edit_custom_gpt,
)
from schemas.common import (
    AssistantMessage,
    ChatHistory,
    ChatSummary,
    CreateOrEditCustomGPTStatus,
    DeleteCustomGPTStatus,
    ExistingCustomGPT,
    UserMessageRequest,
    CustomGptToCreateOrEdit,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(root_path="/api", lifespan=lifespan)

origins = ["https://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conv_id_exists(conv_id: int, session: Session = Depends(get_session)) -> int:
    if session.get(ConversationDB, conv_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conv_id} not found",
        )
    return conv_id

@app.post("/chat-history-by-id", tags=["Chat"], response_model=ChatHistory)
async def get_chat_history(
    chat_id: int,
    session: Session = Depends(get_session),
) -> ChatHistory:
    if session.get(ConversationDB, chat_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {chat_id} not found",
        )
    return retrieve_chat_history_by_id(chat_id, session)

@app.get("/get-chat-summaries", tags=["Chat"], response_model=list[ChatSummary])
async def get_chat_summaries(
    session: Session = Depends(get_session),
) -> list[ChatSummary]:
    return retrieve_chat_summaries_list(session)

@app.post("/send-user-message", tags=["Chat"], response_model=AssistantMessage)
async def send_user_message(
    request: UserMessageRequest,
    session: Session = Depends(get_session),
) -> AssistantMessage:
    if request.conversation_id is not None:
        if session.get(ConversationDB, request.conversation_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found",
            )
    return send_user_message_service(request, session)

@app.get("/retreive-all-custom-gpts", tags=["customGPTs"], response_model=list[ExistingCustomGPT])
async def retreive_all_custom_gpts(
    session: Session = Depends(get_session),
) -> list[ExistingCustomGPT]:
    return get_all_custom_gpts(session)

@app.get("/get-custom-gpt-infos", tags=["customGPTs"], response_model=ExistingCustomGPT)
async def get_custom_gpt_by_id(
    custom_gpt_id: int,
    session: Session = Depends(get_session),
) -> ExistingCustomGPT:
    if session.get(CustomGptsDB, custom_gpt_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom GPT {custom_gpt_id} not found",
        )
    return retrieve_custom_gpt_by_id(custom_gpt_id, session)

@app.delete("/delete-custom-gpt", tags=["customGPTs"], response_model=DeleteCustomGPTStatus)
async def delete_custom_gpt_endpoint(
    custom_gpt_id: int,
    session: Session = Depends(get_session),
) -> DeleteCustomGPTStatus:
    if session.get(CustomGptsDB, custom_gpt_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom GPT {custom_gpt_id} not found",
        )
    return delete_custom_gpt(custom_gpt_id, session)

@app.post("/create-or-edit-custom-gpt", tags=["customGPTs"], response_model=CreateOrEditCustomGPTStatus)
async def create_custom_gpt(
    custom_gpt_infos: CustomGptToCreateOrEdit,
    session: Session = Depends(get_session),
) -> CreateOrEditCustomGPTStatus:
    return create_or_edit_custom_gpt(custom_gpt_infos, session)
