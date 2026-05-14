from typing import Protocol
from uuid import UUID


class FileNotFoundError:
    "File was not found"


class RawFileStorePort(Protocol):
    def add_file(self, file_contents: bytes, file_id: UUID) -> None: ...
    def get_file(self, file_id: UUID) -> bytes: ...
    def delete_file(self, file_id: UUID) -> None: ...
