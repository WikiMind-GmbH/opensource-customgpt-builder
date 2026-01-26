from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class NotFoundError(RuntimeError):
    "This object does not exist"


class QueryError(RuntimeError):
    "Some sort of exception has occured"


class MappingError(QueryError):
    "Mapping failed"


class CustomGPTOverviewDTO(BaseModel):
    id: str
    name: str


class CustomGPTInfosDTO(BaseModel):
    id: str
    name: str
    instructions: str
    description: str


class CgptQueries(Protocol):
    def get_custom_gpt_overviews_ordered_by_created_at(
        self,
    ) -> list[CustomGPTOverviewDTO]: ...
    def get_custom_gpt_infos(self, cgpt_id: str) -> CustomGPTInfosDTO: ...
