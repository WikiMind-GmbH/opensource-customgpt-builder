from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    RelevantDocSnippetRetreiverPort,
)


class retrieveRelevantDocSnippetsAdapter(RelevantDocSnippetRetreiverPort):
    def retreive_doc_snippets(self, query_text: str, cgpt_id: str) -> list[str]:
        return []
