from enum import StrEnum

from pydantic import BaseModel


class RoleQuery(StrEnum):
    user = "user"
    assistant = "assistant"


class SimplifiedMessageQueries(BaseModel):
    role: RoleQuery
    message: str


class ChatHistory(BaseModel):
    custom_gpt_id: str | None
    messages: list[SimplifiedMessageQueries]


class AssistantMessage(BaseModel):
    conversation_id: str
    response_message: SimplifiedMessageQueries


class ChatSummary(BaseModel):
    chat_id: str
    chat_summary: str
