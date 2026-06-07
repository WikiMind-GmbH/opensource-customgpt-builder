from typing import Protocol


class UserHasNoPermissionForCgptOrTheyDontExist(RuntimeError):
    "User has no access to cgpt"


class RelevantDocSnippetRetreiverPort(Protocol):
    """
    For now, we omit any constraints on the structure (length/size) of the returned list
    """

    def retrieve_doc_snippets(self, query_text: str, cgpt_id: str) -> list[str]: ...
