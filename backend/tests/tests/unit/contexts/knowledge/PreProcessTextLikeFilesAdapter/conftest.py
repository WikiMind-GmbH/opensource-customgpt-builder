from pathlib import Path

import pytest


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
