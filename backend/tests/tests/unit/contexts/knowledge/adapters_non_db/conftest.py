from pathlib import Path

import pytest
from fastapi import UploadFile


@pytest.fixture()
def create_tmp_text_file_and_retrun_path():
    text = "This is just some text for the file"
    path = Path("tmp.txt")

    try:
        with open(path, "w") as tmp_file:
            tmp_file.write(text)
            yield path
    finally:
        path.unlink


@pytest.fixture()
def create_tmp_non_text_file_and_retrun_path():
    text = "This is just some text for the file"
    path = Path("tmp.word")

    try:
        with open(path, "w") as tmp_file:
            tmp_file.write(text)
            yield path
    finally:
        path.unlink


@pytest.fixture()
def create_tmp_uploadFile_txt(create_tmp_text_file_and_retrun_path: Path):
    with open(create_tmp_text_file_and_retrun_path, "rb") as file:
        uploadfile = UploadFile(
            file=file, filename=create_tmp_text_file_and_retrun_path.name
        )
        yield uploadfile


@pytest.fixture()
def create_tmp_uploadFile_non_txt(
    create_tmp_non_text_file_and_retrun_path: Path,
):
    with open(create_tmp_non_text_file_and_retrun_path, "rb") as file:
        uploadfile = UploadFile(
            file=file, filename=create_tmp_non_text_file_and_retrun_path.name
        )
        yield uploadfile
