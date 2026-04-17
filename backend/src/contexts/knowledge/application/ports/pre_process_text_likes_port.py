from typing import Protocol

from src.contexts.knowledge.domain.models import UploadedTextLikeFile


class NotUTF8TxtFileError(RuntimeError):
    "File type is not supported to be transformed to text, only utf-8 txt files are supported"


class PreProcessTextLikesPort(Protocol):
    def return_txt_file_contents_as_string(
        self, uploadedTextLikeFile: UploadedTextLikeFile, raw_file_content: bytes
    ) -> str: ...
    def process_document_to_string_based_on_file_type(
        self, uploadedTextLikeFile: UploadedTextLikeFile, raw_file_content: bytes
    ) -> str: ...

    # more file types supported in the future
