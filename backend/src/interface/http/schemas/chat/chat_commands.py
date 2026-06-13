from enum import StrEnum
from typing import Self

from attr import dataclass
from pydantic import BaseModel, ConfigDict, model_validator


class RoleCmd(StrEnum):
    user = "user"
    assistant = "assistant"


@dataclass(frozen=True)
class SimplifiedMessageCmd(BaseModel):
    role: RoleCmd
    message: str


@dataclass(frozen=True)
class AssistantMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    conversation_id: str
    response_message: SimplifiedMessageCmd


@dataclass(frozen=True)
class NewChatRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    request_message: str
    custom_gpt_id: str | None = None
    use_rag: bool = False

    @model_validator(mode="after")
    def validate_rag_requires_custom_gpt(self) -> Self:
        if self.use_rag and self.custom_gpt_id is None:
            raise ValueError("custom_gpt_id must be set when use_rag is true")

        return self


class ContinueChatRequest(BaseModel):
    request_message: str
    conversation_id: str
    use_rag: bool = False


UserMessageRequest = NewChatRequest | ContinueChatRequest
