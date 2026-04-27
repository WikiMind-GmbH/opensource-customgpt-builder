from pathlib import Path

from backend_spanning_helpers import require_env
from src.contexts.knowledge.application.ports.file_storage_port import (
    RawFileStorePort,
)


class RawFileStoreLocalFsAdapter(RawFileStorePort):
    def __init__(
        self, file_storage_folder: Path = Path(require_env("FILE_STORAGE_PATH"))
    ):
        self._file_storage_folder = file_storage_folder

    def add_file(self, file_contents: bytes, file_id: str) -> None:
        file_path: Path = self._file_storage_folder.joinpath(file_id)
        with open(file_path, "wb") as file:
            file.write(file_contents)

    def get_file(self, file_id: str) -> bytes:
        file_path: Path = self._file_storage_folder.joinpath(file_id)
        with open(file_path, "rb") as file:
            return file.read()

    def delete_file(self, file_id: str) -> None:
        file_path: Path = self._file_storage_folder.joinpath(file_id)
        Path.unlink(file_path)
