from typing import Protocol, Sequence

from src.contexts.customGPTs.domain.models import CustomGPT, CustomGPTOverview

# Below: Not needed if we explicitly inherit Protocols -> better for typechecking 
# #@runtime_checkable #So we can  assert isinstance(adapter, port)
class CustomGPTRepository(Protocol):
    def get(self, cgpt_id:str)-> CustomGPT: ...
    def create_cgpt(self, name: str, instructions: str, description: str | None = None)-> CustomGPT: ...
    def delete(self, cgpt: CustomGPT): ...


