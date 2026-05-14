from pathlib import Path

import pytest

from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    ExtractTextFromDocumentPort,
)
from src.contexts.knowledge.infrastructure.adapters.extract_text_from_document_adapter import (
    ExtractTextFromDocumentsAdapter,
)


@pytest.fixture()
def return_byte_content_text_and_of_tmp_txt_file():
    text = "This is just some text for the file"
    path = Path("tmp.txt")

    try:
        with open(path, "w") as tmp_file:
            tmp_file.write(text)
        with open(path, "rb") as contents:
            byte_content = contents.read()
        yield (byte_content, text)
    finally:
        path.unlink()


@pytest.fixture()
def preprocess_port() -> ExtractTextFromDocumentPort:
    files_adapter = ExtractTextFromDocumentsAdapter()
    return files_adapter
