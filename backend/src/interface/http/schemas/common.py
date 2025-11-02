import os
from pathlib import Path
import re
from fastapi import UploadFile
from pydantic import BaseModel, Field, field_validator
from enum import StrEnum

# #---------------------copies of existing helpers because of circular imports..---------------
def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value
#-----------------------------------------------------------------------------------------------

class CustomGPTNameValidated(BaseModel):
    gpt_name: str = Field(max_length=40, min_length=1)

    @field_validator("gpt_name", mode="after")
    @classmethod
    def disallow_illegal_characters(cls, value: str) -> str:
        allowed_pattern = r"^[a-zA-ZäöüÄÖÜß0-9@#._\- ]+$"
        if not re.fullmatch(allowed_pattern, value):
            raise ValueError(
                "Folder name contains illegal characters. Allowed: a-z, A-Z, äöüÄÖÜß, 0-9, space, @, #, ."
            )
        return value

    @field_validator("gpt_name", mode="after")
    @classmethod
    def does_not_start_or_end_with_whitespace(cls, value: str) -> str:
        if value.startswith(" ") or value.endswith(" "):
            raise ValueError("Folder name must not start or end with a space.")
        return value

    @field_validator("gpt_name", mode="after")
    @classmethod
    def forbid_traversal(cls, v: str) -> str:
        p = Path(v)
        if p.is_absolute():
            raise ValueError("Absolute paths are not allowed")
        if ".." in p.parts:
            raise ValueError("Up-level segments (‘..’) are not allowed")
        return v


class CustomGPTFiles(BaseModel):
    filename: str

    @field_validator("filename")
    @classmethod
    def is_jpg_or_heic(cls, v: str) -> str:
        allowed_suffixes: set[str] = set(
            require_env("UPLOAD_ALLOWED_SUFFIXES").split(",")
        )
        suffix = Path(v).suffix.lower()
        if suffix not in allowed_suffixes:
            raise ValueError(
                f"File name must end with {require_env("UPLOAD_ALLOWED_SUFFIXES")}. Other formats are not supported"
            )
        return v


class UploadFileFileFormatValidated(BaseModel):
    """Contains an UploadFile whose .filename is validated to be of the expected formats."""

    uploadFile: UploadFile

    @field_validator("uploadFile", mode="after")
    @classmethod
    def file_name_is_valid_filename(cls, value: UploadFile) -> UploadFile:
        if value.filename == None:
            raise ValueError("File must have a name")
        CustomGPTFiles(filename=value.filename)
        return value


class Role(StrEnum):
    user = "user"
    assistant = "assistant"


class SimplifiedMessage(BaseModel):
    role: Role
    message: str


class ChatHistory(BaseModel):
    custom_gpt_id: str | None
    messages: list[SimplifiedMessage]


class StatusOfStandardResponse(StrEnum):
    success = "success"
    error = "error"

class StandardResponse(BaseModel):
    res: StatusOfStandardResponse


class AssistantMessage(BaseModel):
    conversation_id: str
    response_message: SimplifiedMessage


class ChatSummary(BaseModel):
    chat_id: str
    chat_summary: str
