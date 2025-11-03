from fastapi import APIRouter, Depends
from src.contexts.chat.application.ports.chat_queries import ChatQueries, ConversationOverviewDTO, ConversationTextOnlyDTO
from src.bootstrap import DependenciesContainer
from src.interface.http.deps import deps


from src.interface.http.schemas.chat.chat_queries import ChatHistory, ChatSummary, SimplifiedMessage, Role 

chat_queries_router = APIRouter(prefix="/chat", tags=["Chat: Queries"])

deps: DependenciesContainer = deps

@chat_queries_router.get(
    "/get-chat-summaries",
    response_model=list[ChatSummary],
    operation_id="getChatSummaries",)
def get_chat_summaries(
    queries_adapter: ChatQueries = Depends(deps.chat_queries_adapter_factory),
) -> list[ChatSummary]:
    overviews: list[ConversationOverviewDTO] = queries_adapter.get_chat_summaries_ordered_by_last_message()
    summaries = [ChatSummary(chat_id=ov.id ,chat_summary=ov.title) for ov in overviews]
    return summaries

@chat_queries_router.get(
    "/chat-history-by-id",
    response_model=ChatHistory,
    operation_id="chatHistoryById",
)
async def get_chat_history(
    chat_id: str,
    queries_adapter: ChatQueries = Depends(deps.chat_queries_adapter_factory),
) -> ChatHistory:
    chat: ConversationTextOnlyDTO= queries_adapter.get_chat_history(conv_id=chat_id)
    history_to_old_schema: list[SimplifiedMessage] = [SimplifiedMessage(role = Role(str(msg.role)), message=msg.text) for msg in chat.messages]
    return ChatHistory(custom_gpt_id=chat.customgpt_id, messages=history_to_old_schema)