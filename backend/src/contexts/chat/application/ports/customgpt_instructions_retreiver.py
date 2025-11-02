from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

class DefaultCGPTRetreiverError(RuntimeError):
    "The adapter threw an error"
class CgptNotFoundError(DefaultCGPTRetreiverError):
    "CGPT does not exist"
class RoleDTORetreiver(StrEnum):
    user = "user"
    assistant = "assistant"
    system = 'system'

@dataclass(frozen= True)
class MessageDTORetreiver:
    role: RoleDTORetreiver
    text_content: str

class CustomGPTInstructionsRetreiver(Protocol):
    
    def get_cgpt_sys_prompt(self, cgpt_id: str, ) -> list[MessageDTORetreiver]: ...


