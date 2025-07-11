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
    custom_gpt_id: int | None
    messages: list[SimplifiedMessage]

class StatusOfStandardResponse(StrEnum):
    success = "success"
    error = "error"

class AssistantMessage(BaseModel):
    conversation_id: int
    response_message: SimplifiedMessage

class UserMessageRequest(BaseModel):
    conversation_id: int | None = None
    request_message: SimplifiedMessage
    custom_gpt_id: int | None = None

class CustomGptToCreateOrEdit(BaseModel):
    custom_gpt_id: int | None = None
    custom_gpt_name: str
    custom_gpt_description: str
    custom_gpt_instructions: str

class ExistingCustomGPT(CustomGptToCreateOrEdit):
    custom_gpt_id: int
    created_at: datetime | None

class ChatSummary(BaseModel):
    chat_id: int
    chat_summary: str

class CreateOrEditCustomGPTStatus(BaseModel):
    custom_gpt_id: int | None

class DeleteCustomGPTStatus(BaseModel):
    custom_gpt_id: int | None
