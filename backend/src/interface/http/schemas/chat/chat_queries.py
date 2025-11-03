from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    user = "user"
    assistant = "assistant"


class SimplifiedMessage(BaseModel):
    role: Role
    message: str


class ChatHistory(BaseModel):
    custom_gpt_id: str | None
    messages: list[SimplifiedMessage]


class AssistantMessage(BaseModel):
    conversation_id: str
    response_message: SimplifiedMessage


class ChatSummary(BaseModel):
    chat_id: str
    chat_summary: str