from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    RelevantDocSnippetRetreiverPort,
    UserHasNoPermissionForCgptOrTheyDontExist,
)


class FakeRelevantDocSnippetRetreiverAdapter(RelevantDocSnippetRetreiverPort):
    def __init__(self):
        self._generated_fake_snippets_per_cgpt_id: dict[str, list[str]] = {}
        self._number_of_times_retrieve_snippets_was_called_with_cgpt_id: dict[
            str, int
        ] = {}

    def set_fake_snippet_to_return_for_cgpt_id(
        self, cgpt_id: str, returned_snippets_texts: list[str]
    ):
        self._generated_fake_snippets_per_cgpt_id[cgpt_id] = returned_snippets_texts
        self._number_of_times_retrieve_snippets_was_called_with_cgpt_id[cgpt_id] = 0

    def get_number_of_times_retrieve_doc_snippets_got_called_with(self, cgpt_id: str):
        return self._number_of_times_retrieve_snippets_was_called_with_cgpt_id[cgpt_id]

    def retrieve_doc_snippets(self, query_text: str, cgpt_id: str) -> list[str]:
        if cgpt_id not in self._generated_fake_snippets_per_cgpt_id.keys():
            raise UserHasNoPermissionForCgptOrTheyDontExist()
        self._number_of_times_retrieve_snippets_was_called_with_cgpt_id[cgpt_id] += 1
        return self._generated_fake_snippets_per_cgpt_id[cgpt_id]
