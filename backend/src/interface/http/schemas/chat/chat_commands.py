from enum import StrEnum
from pydantic import BaseModel


class Role(StrEnum):
    user = "user"
    assistant = "assistant"


class SimplifiedMessage(BaseModel):
    role: Role
    message: str


class AssistantMessage(BaseModel):
    conversation_id: str
    response_message: SimplifiedMessage



class NewChatRequest(BaseModel):
    request_message: str
    custom_gpt_id: str | None

class ContinueChatRequest(BaseModel):
    request_message: str
    conversation_id: str

UserMessageRequest = NewChatRequest | ContinueChatRequest