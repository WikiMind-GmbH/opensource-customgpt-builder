from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.chat_queries import (
    ConversationOverviewDTO,
    ConversationTextOnlyDTO,
    NotFoundError,
    RoleDTO,
)
from src.interface.http.schemas.chat.chat_queries import (
    ChatHistory,
    ChatSummary,
    RoleQuery,
    SimplifiedMessageQueries,
)


def register_query_exception_handlers_queries_port(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(_, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"Conversation not found: {getattr(exc, 'args', [''])[0]}"
            },
        )


def conversationOverviewsDTO_to_chatSummaries(
    conv_overviews: list[ConversationOverviewDTO],
) -> list[ChatSummary]:
    summaries: list[ChatSummary] = [
        ChatSummary(chat_id=ov.id, chat_summary=ov.title) for ov in conv_overviews
    ]
    return summaries


def conversationTextOnlyDTO_to_chat(conv: ConversationTextOnlyDTO) -> ChatHistory:
    if any(m.role is RoleDTO.system for m in conv.messages):
        raise RuntimeError("Should not be used on data cotaining system prompts")
    simplified_messages: list[SimplifiedMessageQueries] = [
        SimplifiedMessageQueries(role=RoleQuery(str(msg.role)), message=msg.text)
        for msg in conv.messages
    ]
    return ChatHistory(custom_gpt_id=conv.customgpt_id, messages=simplified_messages)
