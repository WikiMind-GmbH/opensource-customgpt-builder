from typing import Protocol


class CustomGPTInstructionsRetreiver(Protocol):

    def get_cgpt_name_and_instructions(self, gpt_id: str) -> tuple[str, str]: ...
