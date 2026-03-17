from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class RoleDTOllm(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


@dataclass
class MessageDTOllm:
    role: RoleDTOllm
    imageUrlOrText: str


class NoAssistantResponse(RuntimeError):
    "API did not return anything"


class ErrorWhileCallingAPI(RuntimeError):
    "Error occured when calling the api"


class LlmPort(Protocol):
    def get_assistant_text_response(
        self,
        messages_dto: list[MessageDTOllm],
    ) -> str: ...
