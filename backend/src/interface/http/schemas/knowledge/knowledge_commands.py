from pathlib import Path

from fastapi import UploadFile
from pydantic import BaseModel, field_validator

from backend_spanning_helpers import require_env


class UploadFileForKnowledgeContext(BaseModel):
    """Contains an UploadFile whose .filename is validated to be of the expected formats."""

    uploadFile: UploadFile
    gpt_ids: list[str]

    @field_validator("uploadFile", mode="after")
    @classmethod
    def file_suffix_is_supported(cls, value: UploadFile) -> UploadFile:
        if value.filename is None:
            raise ValueError("Filename must not be empty")
        suffix = Path(value.filename).suffix.lower()
        supported_file_types = set(require_env("UPLOAD_ALLOWED_SUFFIXES").split(","))
        if suffix not in supported_file_types:
            raise ValueError(
                f"File name must end with {require_env('UPLOAD_ALLOWED_SUFFIXES')}. Other formats are not supported"
            )
        return value

    # @field_validator("uploadFile", mode="after")
    # @classmethod
    # def file_size_ok(cls, value: UploadFile) -> UploadFile:
    #     max_size: int = int(require_env("UPLOAD_MAX_FILE_SIZE"))

    #     contents = await value.read()
    #     if (
    #         len(contents) > max_size
    #     ):  # better: https://github.com/fastapi/fastapi/issues/362#issuecomment-584104025
    #         raise ValueError("File too large")  # http 413
