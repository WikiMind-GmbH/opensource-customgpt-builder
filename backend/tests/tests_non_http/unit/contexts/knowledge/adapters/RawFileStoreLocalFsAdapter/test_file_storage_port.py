from uuid import uuid4

import pytest

from src.contexts.knowledge.application.ports.file_storage_port import (
    FileNotFoundError,
    RawFileStorePort,
)


def test_add_file_and_get_file_roundtrip(
    file_storage_adapter: RawFileStorePort,
) -> None:
    file_id = uuid4()
    file_contents = b"hello world"

    file_storage_adapter.add_file(
        file_id=file_id,
        file_contents=file_contents,
    )

    result = file_storage_adapter.get_file(file_id)

    assert result == file_contents


def test_add_file_and_get_file_roundtrip_with_arbitrary_binary_bytes(
    file_storage_adapter: RawFileStorePort,
) -> None:
    file_id = uuid4()
    file_contents = bytes([0, 159, 255, 10, 13, 80, 75, 3, 4])

    file_storage_adapter.add_file(
        file_id=file_id,
        file_contents=file_contents,
    )

    result = file_storage_adapter.get_file(file_id)

    assert result == file_contents


def test_delete_file_removes_file(
    file_storage_adapter: RawFileStorePort,
) -> None:
    file_id = uuid4()
    file_contents = b"hello world"

    file_storage_adapter.add_file(
        file_id=file_id,
        file_contents=file_contents,
    )

    file_storage_adapter.delete_file(file_id)

    with pytest.raises(FileNotFoundError):
        file_storage_adapter.get_file(file_id)


def test_get_file_raises_when_file_does_not_exist(
    file_storage_adapter: RawFileStorePort,
) -> None:
    with pytest.raises(FileNotFoundError):
        file_storage_adapter.get_file(uuid4())


def test_delete_file_raises_when_file_does_not_exist(
    file_storage_adapter: RawFileStorePort,
) -> None:
    with pytest.raises(FileNotFoundError):
        file_storage_adapter.delete_file(uuid4())
