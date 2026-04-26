from typing import assert_never

from src.contexts.knowledge.application.ports.pre_process_text_likes_port import (
    SupportedFileTypesEnum,
)
from src.contexts.knowledge.domain.models import TextFileTypeEnum


class PreProcessTextLikesPortMapper:
    @staticmethod
    def adapter_to_domain_file_types(
        adapter_type: SupportedFileTypesEnum,
    ) -> TextFileTypeEnum:
        match adapter_type:
            case SupportedFileTypesEnum.txt:
                return TextFileTypeEnum.txt
            case _:
                assert_never(adapter_type)

    @staticmethod
    def domain_to_adapter_file_types(
        domain_type: TextFileTypeEnum,
    ) -> SupportedFileTypesEnum:
        match domain_type:
            case TextFileTypeEnum.txt:
                return SupportedFileTypesEnum.txt
            case _:
                assert_never(domain_type)
