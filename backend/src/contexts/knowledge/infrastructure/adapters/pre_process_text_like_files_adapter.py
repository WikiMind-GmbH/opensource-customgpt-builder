from typing import assert_never

from src.contexts.knowledge.application.ports.pre_process_text_likes_port import (
    NotUTF8TxtFileError,
    PreProcessTextLikesPort,
    SupportedFileTypesEnum,
)


class PreProcessTextLikeFilesAdapter(PreProcessTextLikesPort):
    def _return_txt_file_contents_as_string(
        self, file_type: SupportedFileTypesEnum, raw_file_content: bytes
    ) -> str:
        if not file_type == SupportedFileTypesEnum.txt:
            raise NotUTF8TxtFileError("Not a txt file")
        try:
            return raw_file_content.decode()
        except UnicodeDecodeError:
            raise NotUTF8TxtFileError("txt file not encoded in utf-8")
        except Exception as e:
            raise e

    def process_document_to_string_based_on_file_type(
        self, file_type: SupportedFileTypesEnum, raw_file_content: bytes
    ) -> str:
        match file_type:
            case SupportedFileTypesEnum.txt:
                return self._return_txt_file_contents_as_string(
                    file_type=file_type,
                    raw_file_content=raw_file_content,
                )
            case _:
                assert_never(file_type)
