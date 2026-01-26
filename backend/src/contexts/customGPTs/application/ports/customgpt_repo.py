from typing import Protocol

from src.contexts.customGPTs.domain.models import CustomGPT


class CgptNotFound(RuntimeError):
    "Custom Gpt of that id not found in DB"


class CustomGPTRepository(Protocol):
    def get(self, cgpt_id: str) -> CustomGPT: ...
    def create_cgpt(
        self, name: str, instructions: str, description: str | None = None
    ) -> CustomGPT: ...
    def delete(self, cgpt_id: str): ...
