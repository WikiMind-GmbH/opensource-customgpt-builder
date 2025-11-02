from pydantic import BaseModel


class NewChatRequest(BaseModel):
    request_message: str
    custom_gpt_id: str | None

class ContinueChatRequest(BaseModel):
    request_message: str
    conversation_id: str

UserMessageRequest = NewChatRequest | ContinueChatRequest