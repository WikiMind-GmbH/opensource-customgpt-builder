from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel

class Role(StrEnum):
    user = "user"
    assistant = "assistant"

class SimplifiedMessage(BaseModel):
    role: Role
    message: str

class ChatHistory(BaseModel):
    messages: list[SimplifiedMessage]
    created_at: datetime
    last_modified: datetime



class ChatsOverview:
    chat_name: str
    created_at: datetime
    last_modified: datetime


