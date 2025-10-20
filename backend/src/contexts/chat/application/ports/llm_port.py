from typing import Protocol
from src.contexts.chat.domain.models import Message

class NoAssistantResponse(RuntimeError):
    "API did not return anything"

class ErrorWhileCallingAPI(RuntimeError):
    "Error occured when calling the api"

class LlmPort(Protocol):
    def get_assistant_response(self, messages_excluding_sys_prompt: list[Message], cgpt_systemprompt: list[Message])->str: ...
