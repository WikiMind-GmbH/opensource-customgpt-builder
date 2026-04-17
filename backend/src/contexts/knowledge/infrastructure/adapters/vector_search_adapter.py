from src.contexts.knowledge.application.ports.search_port import MetadataDTO, TextSearch, TextSnippetDTO


class Vectorsearch(TextSearch):
    def __init__(self) -> None:
        # vector store db url
        pass

    def add_chunk(self, text_chunk: str, metadata: MetadataDTO) -> None:


    def return_relevant_text_snippets(self, customGPT_id: str | None = None, max_snippets: int = 5) -> list[TextSnippetDTO]:

