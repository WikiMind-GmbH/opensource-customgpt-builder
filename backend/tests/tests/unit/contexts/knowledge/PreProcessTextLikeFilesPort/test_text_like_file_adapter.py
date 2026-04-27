from src.contexts.knowledge.application.ports.pre_process_text_likes_port import (
    PreProcessTextLikesPort,
    SupportedFileTypesEnum,
)


def test_correctly_reads_text(
    return_byte_content_text_and_of_tmp_txt_file: tuple[bytes, str],
    preprocess_port: PreProcessTextLikesPort,
):
    bytes_content, text = return_byte_content_text_and_of_tmp_txt_file
    text_read_by_adapter = (
        preprocess_port.process_document_to_string_based_on_file_type(
            file_type=SupportedFileTypesEnum.txt, raw_file_content=bytes_content
        )
    )
    assert text_read_by_adapter == text
