from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    ExtractTextFromDocumentPort,
    SupportedFileTypesEnum,
)


def test_correctly_reads_text(
    return_byte_content_text_and_of_tmp_txt_file: tuple[bytes, str],
    preprocess_port: ExtractTextFromDocumentPort,
):
    bytes_content, text = return_byte_content_text_and_of_tmp_txt_file
    text_read_by_adapter = (
        preprocess_port.process_document_to_string_based_on_file_type(
            file_type=SupportedFileTypesEnum.txt, raw_file_content=bytes_content
        )
    )
    assert text_read_by_adapter == text
