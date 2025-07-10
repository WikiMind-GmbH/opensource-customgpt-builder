from pydantic import BaseModel
from enum import StrEnum
from datetime import datetime

class Role(StrEnum):
    user = "user"
    assistant = "assistant"

class SimplifiedMessage(BaseModel):
    role: Role
    message: str
    
class ChatHistory(BaseModel):
    custom_gpt_id: int
    messages: list[SimplifiedMessage]

class RetreiveChatHistory(BaseModel):
    chat_id: int


class StatusOfStandardResponse(StrEnum):
    success = "success"
    error = "error"

# response: response from assistant model
class AssistantMessage(BaseModel):
    conversation_id: int
    response_message: str

class UserMessageRequest(BaseModel):
    message: str
    model_id: int

class CustomGPTInfos(BaseModel):
    custom_gpt_name: str
    custom_gpt_description: str
    custom_gpt_instructions: str

class ExistingCustomGPT(CustomGPTInfos):
    custom_gpt_id: int
    created_at: datetime | None

# one liners for chat list
class ChatSummary(BaseModel):
    chat_id: int
    chat_summary: str
    
class ExistingCustomGPTOverview(BaseModel):
    custom_gpt_id: int
    custom_gpt_name: str

class CreateCustomGPTResponse(BaseModel):
    custom_gpt_id: int | None
    status: bool



