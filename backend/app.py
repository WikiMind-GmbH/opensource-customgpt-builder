from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlmodel import Session

from src.contexts.chat.application.exceptions import ConversationNonExistentError
from src.bootstrap import DependenciesContainer
from src.contexts.chat.application.ports.uow import ConversationUOW
from src.contexts.chat.application.service_layer.service_functions import get_chat_summaries_service, retrieve_chat_history_by_id
from src.contexts.chat.domain.models import ConversationFilteredForClient, ConversationOverview
from src.interface.http.deps import deps
from backend_spanning_helpers import require_env, validateFileFormat, validateGptExistsQuery
from models.models import ConversationDB
from services.database import create_db_and_tables, get_session
from services.chats_service import (
    send_user_message_service,
)
from services.custom_gpt_service import (
    add_files_to_gpt_helper,
    get_all_custom_gpts,
    list_loaded_files,
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
    Role,
    SimplifiedMessage,
    StandardResponse,
    UploadFileFileFormatValidated,
    UserMessageRequest,
    CustomGptToCreateOrEdit,
)
LOADED_FILES_PATH = require_env("LOADED_FILES_PATH")

deps: DependenciesContainer = deps

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(root_path="/api", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # return PlainTextResponse(str(exc), status_code=400)
    # pick just the first error
    error = exc.errors()[0]
    # error["loc"] is like ["body","custom_gpt_description"]
    field = ".".join(str(x) for x in error["loc"][1:])
    msg = f"{field}: {error['msg']}"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": msg},
    )

@app.exception_handler(ConversationNonExistentError)
async def validation_exception_handler(
    request: Request, exc: ConversationNonExistentError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Conversation does not exist"},
    )

origins = ["https://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Refactored:
#------------------------------------------------------------------------ 

@app.get(
    "/get-chat-summaries",
    tags=["Chat"],
    response_model=list[ChatSummary],
    operation_id="getChatSummaries",)
def get_chat_summaries(
    chat_uow: ConversationUOW = Depends(deps.conversation_uow_factory),
) -> list[ChatSummary]:
    overviews: List[ConversationOverview] = get_chat_summaries_service(chat_uow)
    summaries = [ChatSummary(chat_id=ov.id,chat_summary=ov.title) for ov in overviews]
    return summaries#

# Ongoing:
#------------------------------------------------------------------------ 

@app.post(
    "/chat-history-by-id",
    tags=["Chat"],
    response_model=ChatHistory,
    operation_id="chatHistoryById",
)
async def get_chat_history(
    chat_id: str,
    chat_uow: ConversationUOW = Depends(deps.conversation_uow_factory),
) -> ChatHistory:
    history:ConversationFilteredForClient = retrieve_chat_history_by_id(chat_id, chat_uow)
    messages_translated: list[SimplifiedMessage] = [SimplifiedMessage(role = Role(str(msg.role)), message=msg.text) for msg in history.messages]
    return ChatHistory(custom_gpt_id=history.customgpt_id, messages=messages_translated)
#------------------------------------------------------------------------ 




    # decoupling
    # return retrieve_chat_summaries_list(session)

@app.post(
    "/send-user-message",
    tags=["Chat"],
    response_model=AssistantMessage,
    operation_id="sendUserMessage",
)
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

@app.get(
    "/retreive-all-custom-gpts",
    tags=["customGPTs"],
    response_model=list[ExistingCustomGPT],
    operation_id="retreiveAllCustomGpts",
)
async def retreive_all_custom_gpts(
    session: Session = Depends(get_session),
) -> list[ExistingCustomGPT]:
    return await get_all_custom_gpts(session)

@app.get(
    "/get-custom-gpt-infos",
    tags=["customGPTs"],
    response_model=ExistingCustomGPT,
    operation_id="getCustomGptInfos",
)
async def get_custom_gpt_by_id(
    custom_gpt_id: int= Depends(validateGptExistsQuery),
    session: Session = Depends(get_session),
) -> ExistingCustomGPT:
    return retrieve_custom_gpt_by_id(custom_gpt_id, session)

@app.delete(
    "/delete-custom-gpt",
    tags=["customGPTs"],
    response_model=DeleteCustomGPTStatus,
    operation_id="deleteCustomGpt",
)
async def delete_custom_gpt_endpoint(
    custom_gpt_id: int = Depends(validateGptExistsQuery),
    session: Session = Depends(get_session),
) -> DeleteCustomGPTStatus:
    return delete_custom_gpt(custom_gpt_id, session)

@app.post(
    "/create-or-edit-custom-gpt",
    tags=["customGPTs"],
    response_model=CreateOrEditCustomGPTStatus,
    operation_id="createOrEditCustomGpt",
)
async def create_custom_gpt(
    custom_gpt_infos: CustomGptToCreateOrEdit,
    session: Session = Depends(get_session),
) -> CreateOrEditCustomGPTStatus:
    return await create_or_edit_custom_gpt(custom_gpt_infos, session)

@app.post(
    "/add-files-to-gpt",
    tags=["customGPTs"],
    response_model=StandardResponse,
    operation_id="addFilesToGpt",
)
async def add_files_to_gpt(
    validated_custom_gpt_id: int = Depends(validateGptExistsQuery),
    validated_files: list[UploadFileFileFormatValidated] = Depends(validateFileFormat),
    session: Session = Depends(get_session),
) -> StandardResponse:
    res: StandardResponse = await add_files_to_gpt_helper(
        validated_custom_gpt_id=validated_custom_gpt_id,
        validated_files=validated_files,
        session=session
    )
    return res

@app.get("/gpts/{custom_gpt_id}/files", response_model=list[str], tags=["customGPTs"], operation_id="listFilesToGpt",)
async def get_files(custom_gpt_id: int):
    return list_loaded_files(custom_gpt_id)