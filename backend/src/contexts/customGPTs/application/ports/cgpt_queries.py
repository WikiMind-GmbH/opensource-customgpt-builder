from typing import Protocol
from src.contexts.customGPTs.application.ports.customgpt_uow import CgptUOW
from pydantic import BaseModel


class CustomGPTOverviewDTO(BaseModel):
    id: str
    name: str

class CustomGPTInfosDTO(BaseModel):
    id: str
    name: str
    instructions: str
    description: str

class CgptQueries(Protocol):
    def get_custom_gpt_overviews(self)-> list[CustomGPTOverviewDTO]:...
    def get_custom_gpt_infos(self, cgpt_id:str)->CustomGPTInfosDTO:...