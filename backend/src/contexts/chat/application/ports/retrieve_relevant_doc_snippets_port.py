from typing import Protocol


class RelevantDocSnippetRetreiverPort(Protocol):
    """
    For now, we omit any constraints on the structure (length/size) of the returned list
    """

    def retreive_doc_snippets(self, query_text: str, cgpt_id: str) -> list[str]: ...
