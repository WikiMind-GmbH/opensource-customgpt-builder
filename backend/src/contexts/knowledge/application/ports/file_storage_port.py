from typing import Protocol


class ErrorWhileStoring(RuntimeError):
    "An error occured while trying to store the document"


class ErrorWhileRetrieving(RuntimeError):
    "An error occured while trying to retrieve the document"


class RawFileStorePort(Protocol):
    def add_file(self, file_contents: bytes, file_id: str) -> None: ...
    def get_file(self, file_id: str) -> bytes: ...
    def delete_file(self, id: str) -> None: ...
