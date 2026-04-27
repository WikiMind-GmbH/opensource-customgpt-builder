from pathlib import Path

import pytest

from src.contexts.knowledge.application.ports.pre_process_text_likes_port import (
    PreProcessTextLikesPort,
)
from src.contexts.knowledge.infrastructure.adapters.pre_process_text_like_files_adapter import (
    PreProcessTextLikeFilesAdapter,
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
def preprocess_port() -> PreProcessTextLikesPort:
    files_adapter = PreProcessTextLikeFilesAdapter()
    return files_adapter
