from pathlib import Path
from typing import Iterator

import pytest

from src.contexts.knowledge.application.ports.file_storage_port import RawFileStorePort
from src.contexts.knowledge.infrastructure.adapters.local_file_system_storage_adapter import (
    RawFileStoreLocalFsAdapter,
)


@pytest.fixture()
def file_storage_adapter(tmp_path: Path) -> Iterator[RawFileStorePort]:
    adapter = RawFileStoreLocalFsAdapter(tmp_path)

    yield adapter
