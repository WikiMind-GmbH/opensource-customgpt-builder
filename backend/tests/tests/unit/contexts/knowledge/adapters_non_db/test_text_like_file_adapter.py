from fastapi import UploadFile

from src.contexts.knowledge.infrastructure.adapters.pre_process_text_like_files_adapter import (
    PreProcessTextLikeFilesAdapter,
)


def test_correctly_checks_file_type(create_tmp_uploadFile_txt: UploadFile):
    files_adapter = PreProcessTextLikeFilesAdapter()
    assert files_adapter.return_true_if_file_is_txt_file(create_tmp_uploadFile_txt)
