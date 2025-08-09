import os
from pathlib import Path
import re
from fastapi import HTTPException, UploadFile, status
from pydantic import BaseModel, Field, field_validator
from enum import StrEnum
from datetime import datetime

from services.database import get_session
from models.models import CustomGptsDB

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
    custom_gpt_id: int | None
    messages: list[SimplifiedMessage]


class StatusOfStandardResponse(StrEnum):
    success = "success"
    error = "error"

class StandardResponse(BaseModel):
    res: StatusOfStandardResponse


class AssistantMessage(BaseModel):
    conversation_id: int
    response_message: SimplifiedMessage


class UserMessageRequest(BaseModel):
    conversation_id: int | None = None
    request_message: str
    custom_gpt_id: int | None = None


class CustomGptToCreateOrEdit(BaseModel):
    custom_gpt_id: int | None = None
    custom_gpt_name: str = Field(max_length=40, min_length=1) # ToDo: Handle this nicely -is possible like that for nice client errors or not?
    custom_gpt_description: str = Field(max_length=200, min_length=1)
    custom_gpt_instructions: str = Field(max_length=50000, min_length=1)

    @field_validator("custom_gpt_name", mode="after")
    @classmethod
    def name_is_valid(cls, custom_gpt_name:str)-> str:
        validated =  CustomGPTNameValidated(gpt_name=custom_gpt_name)
        return validated.gpt_name
    
    @field_validator("custom_gpt_id", mode="after")
    @classmethod
    def gptExistsIfIdGiven(cls, custom_gpt_id:int):
        if(custom_gpt_id):
            session = next(get_session())
            try:
                if session.get(CustomGptsDB, custom_gpt_id) is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Conversation {custom_gpt_id} not found",
                    )
                return custom_gpt_id
            finally:
                session.close()




class ExistingCustomGPT(CustomGptToCreateOrEdit):
    custom_gpt_id: int
    created_at: datetime | None


class ChatSummary(BaseModel):
    chat_id: int
    chat_summary: str


class CreateOrEditCustomGPTStatus(BaseModel):
    custom_gpt_id: int | None


class DeleteCustomGPTStatus(BaseModel):
    custom_gpt_id: int | None


class CustomGPT(BaseModel):
    id: int | None = None
    name: CustomGPTNameValidated
    custom_gpt_description: str
    custom_gpt_instructions: str

    def to_db(self) -> CustomGptsDB:
        return CustomGptsDB(
            id=self.id,
            name=self.name.gpt_name,
            custom_gpt_description=self.custom_gpt_description,
            custom_gpt_instructions=self.custom_gpt_description,
        )


class CustomGPTCreated(CustomGPT):
    id: int

    @classmethod
    def from_db(cls, model: CustomGptsDB)->'CustomGPTCreated':
        return CustomGPTCreated(
            id=model.id,
            name=CustomGPTNameValidated(gpt_name=model.name),
            custom_gpt_description=model.custom_gpt_description,
            custom_gpt_instructions=model.custom_gpt_description,
        )
