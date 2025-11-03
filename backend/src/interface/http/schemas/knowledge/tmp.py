
from pathlib import Path
from fastapi import UploadFile
from pydantic import BaseModel, field_validator

from backend_spanning_helpers import require_env
    


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