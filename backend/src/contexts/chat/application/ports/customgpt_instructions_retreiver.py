from dataclasses import dataclass
from typing import Protocol


class DefaultCGPTRetreiverError(RuntimeError):
    "The adapter threw an error"


class CgptNotFoundError(DefaultCGPTRetreiverError):
    "CGPT does not exist"


@dataclass(frozen=True)
class CustomGPTInfosDTO:
    name: str
    instructions: str


class CustomGPTInstructionsRetreiver(Protocol):
    def get_cgpt_infos_for_prompt(
        self,
        cgpt_id: str,
    ) -> CustomGPTInfosDTO: ...
