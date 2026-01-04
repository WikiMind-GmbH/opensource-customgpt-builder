from fastapi import APIRouter, Depends
from backend_spanning_helpers import require_env
from src.interface.http.mappers_data_and_exceptions.chat.chat_queries_classes_and_exceptions import conversationOverviewsDTO_to_chatSummaries, conversationTextOnlyDTO_to_chat
from src.contexts.chat.application.ports.chat_queries import ChatQueries, ConversationOverviewDTO, ConversationTextOnlyDTO
from src.bootstrap import DependenciesContainer
from backend.src.interface.http.composition import dependencies_container


from src.interface.http.schemas.chat.chat_queries import ChatHistory, ChatSummary

chat_queries_router = APIRouter(prefix="/chat", tags=["Chat: Queries"])

dependencies_container: DependenciesContainer = dependencies_container

@chat_queries_router.get(
    "/get-chat-summaries",
    response_model=list[ChatSummary],
    operation_id="getChatSummaries",)
def get_chat_summaries(
    queries_adapter: ChatQueries = Depends(dependencies_container.chat_queries_adapter_factory),
) -> list[ChatSummary]:
    overviews: list[ConversationOverviewDTO] = queries_adapter.get_chat_summaries_ordered_by_last_message()
    summaries: list[ChatSummary] = conversationOverviewsDTO_to_chatSummaries(overviews)
    return summaries

@chat_queries_router.get(
    "/chat-history-by-id",
    response_model=ChatHistory,
    operation_id="chatHistoryById",
)
async def get_chat_history(
    chat_id: str,
    queries_adapter: ChatQueries = Depends(dependencies_container.chat_queries_adapter_factory),
) -> ChatHistory:
    chat: ConversationTextOnlyDTO= queries_adapter.get_chat_history(conv_id=chat_id)
    chat_history: ChatHistory = conversationTextOnlyDTO_to_chat(chat)
    return chat_history