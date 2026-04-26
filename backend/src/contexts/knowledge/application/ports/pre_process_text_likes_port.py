from enum import StrEnum
from typing import Protocol


class NotUTF8TxtFileError(RuntimeError):
    "File type is not supported to be transformed to text, only utf-8 txt files are supported"


class SupportedFileTypesEnum(StrEnum):
    txt = "txt"


class PreProcessTextLikesPort(Protocol):
    def _return_txt_file_contents_as_string(
        self, file_type: SupportedFileTypesEnum, raw_file_content: bytes
    ) -> str: ...
    def process_document_to_string_based_on_file_type(
        self, file_type: SupportedFileTypesEnum, raw_file_content: bytes
    ) -> str: ...

    # more file types supported in the future
