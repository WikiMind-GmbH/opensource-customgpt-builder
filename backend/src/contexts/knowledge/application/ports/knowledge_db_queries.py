from typing import Protocol


class KnowledgeDBQueriesPort(Protocol):
    def check_if_hash_already_exists(self, hash: str) -> bool: ...
