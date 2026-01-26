from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class NotFoundError(RuntimeError):
    "This object does not exist"


class RoleDTO(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


@dataclass
class TextMessageDTO:
    role: RoleDTO
    text: str


@dataclass
class ConversationTextOnlyDTO:
    customgpt_id: str | None
    messages: list[TextMessageDTO]


@dataclass
class ConversationOverviewDTO:
    id: str
    title: str = ""


class ChatQueries(Protocol):
    def get_chat_summaries_ordered_by_last_message(
        self,
    ) -> list[ConversationOverviewDTO]: ...
    def get_chat_history(self, conv_id: str) -> ConversationTextOnlyDTO: ...
