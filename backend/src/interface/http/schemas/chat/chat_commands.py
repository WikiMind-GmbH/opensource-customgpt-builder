from enum import StrEnum
from pydantic import BaseModel


class RoleCmd(StrEnum):
    user = "user"
    assistant = "assistant"


class SimplifiedMessageCmd(BaseModel):
    role: RoleCmd
    message: str


class AssistantMessage(BaseModel):
    conversation_id: str
    response_message: SimplifiedMessageCmd



class NewChatRequest(BaseModel):
    request_message: str
    custom_gpt_id: str | None

class ContinueChatRequest(BaseModel):
    request_message: str
    conversation_id: str

UserMessageRequest = NewChatRequest | ContinueChatRequest