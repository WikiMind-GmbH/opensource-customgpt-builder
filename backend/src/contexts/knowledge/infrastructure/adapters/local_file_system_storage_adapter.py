from pathlib import Path
from uuid import UUID

from backend_spanning_helpers import require_env
from src.contexts.knowledge.application.ports.file_storage_port import (
    FileNotFoundError as PortFileNotFoundError,
)
from src.contexts.knowledge.application.ports.file_storage_port import (
    RawFileStorePort,
)


class RawFileStoreLocalFsAdapter(RawFileStorePort):
    def __init__(
        self, file_storage_folder: Path = Path(require_env("FILE_STORAGE_PATH"))
    ):
        self._file_storage_folder = file_storage_folder

    def add_file(self, file_contents: bytes, file_id: UUID) -> None:
        file_path: Path = self._file_storage_folder.joinpath(str(file_id))
        with open(file_path, "wb") as file:
            file.write(file_contents)

    def get_file(self, file_id: UUID) -> bytes:
        file_path: Path = self._file_storage_folder.joinpath(str(file_id))
        try:
            with open(file_path, "rb") as file:
                return file.read()
        except FileNotFoundError as exc:
            raise PortFileNotFoundError(f"File {file_id} was not found") from exc

    def delete_file(self, file_id: UUID) -> None:
        file_path: Path = self._file_storage_folder.joinpath(str(file_id))
        try:
            Path.unlink(file_path)
        except FileNotFoundError as exc:
            raise PortFileNotFoundError(f"File {file_id} was not found") from exc
