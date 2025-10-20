from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, Sequence
from src.contexts.chat.domain.models import Message

class DefaultCGPTRetreiverError(RuntimeError):
    "The adapter threw an error"
class CgptNotFoundError(DefaultCGPTRetreiverError):
    "CGPT does not exist"
class RoleDTO(StrEnum):
    user = "user"
    assistant = "assistant"
    system = 'system'

@dataclass(frozen= True)
class MessageDTO:
    role: RoleDTO
    text_content: str

class CustomGPTInstructionsRetreiver(Protocol):
    
    def get_cgpt_sys_prompt(self, cgpt_id: str, ) -> list[MessageDTO]: ...


