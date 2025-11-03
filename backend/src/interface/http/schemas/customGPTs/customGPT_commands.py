from pathlib import Path
import re
from pydantic import BaseModel, Field, field_validator


class CustomGptToCreate(BaseModel):
    custom_gpt_name: str = Field(max_length=40, min_length=1) # ToDo: Handle this nicely -is possible like that for nice client errors or not?
    custom_gpt_description: str = Field(max_length=200, min_length=1)
    custom_gpt_instructions: str = Field(max_length=50000, min_length=1)

class CustomGptToEdit(BaseModel):
    custom_gpt_id: str
    custom_gpt_name: str = Field(max_length=40, min_length=1) # ToDo: Handle this nicely -is possible like that for nice client errors or not?
    custom_gpt_description: str = Field(max_length=200, min_length=1)
    custom_gpt_instructions: str = Field(max_length=50000, min_length=1)

    # @field_validator("custom_gpt_name", mode="after")
    # @classmethod
    # def disallow_illegal_characters(cls, value: str) -> str:
    #     allowed_pattern = r"^[a-zA-ZäöüÄÖÜß0-9@#._\- ]+$"
    #     if not re.fullmatch(allowed_pattern, value):
    #         raise ValueError(
    #             "Folder name contains illegal characters. Allowed: a-z, A-Z, äöüÄÖÜß, 0-9, space, @, #, ."
    #         )
    #     return value

    # @field_validator("custom_gpt_name", mode="after")
    # @classmethod
    # def does_not_start_or_end_with_whitespace(cls, value: str) -> str:
    #     if value.startswith(" ") or value.endswith(" "):
    #         raise ValueError("Folder name must not start or end with a space.")
    #     return value

    # @field_validator("custom_gpt_name", mode="after")
    # @classmethod
    # def forbid_traversal(cls, v: str) -> str:
    #     p = Path(v)
    #     if p.is_absolute():
    #         raise ValueError("Absolute paths are not allowed")
    #     if ".." in p.parts:
    #         raise ValueError("Up-level segments (‘..’) are not allowed")
    #     return v