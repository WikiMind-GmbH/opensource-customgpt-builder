from collections.abc import Iterable

import pytest
from fastapi import FastAPI

from src.contexts.chat.application.ports.chat_queries import (
    NotFoundError as ChatNotFoundError,
)
from src.contexts.chat.application.ports.chat_repo import (
    ConversationNotFoundError,
    TemporaryConvRepoError,
)
from src.contexts.chat.application.ports.customgpt_instructions_retreiver import (
    CgptNotFoundError,
    DefaultCGPTRetreiverError,
)
from src.contexts.chat.application.ports.llm_port import (
    ErrorWhileCallingAPI,
    NoAssistantResponse,
)
from src.contexts.chat.application.ports.retrieve_relevant_doc_snippets_port import (
    UserHasNoPermissionForCgptOrTheyDontExist as ChatCgptPermissionError,
)
from src.contexts.customGPTs.application.ports.cgpt_queries import (
    MappingError,
    QueryError,
)
from src.contexts.customGPTs.application.ports.cgpt_queries import (
    NotFoundError as CgptNotFoundQueryError,
)
from src.contexts.customGPTs.application.ports.customgpt_repo import CgptNotFound
from src.contexts.knowledge.application.ports.cgpt_permissions_port import (
    EmptyListToCheckPassedError,
    UserHasNoPermissionForCgptOrTheyDontExist,
)
from src.contexts.knowledge.application.ports.embedding_generator_port import (
    EmbeddingProviderError,
)
from src.contexts.knowledge.application.ports.extract_text_from_document_port import (
    NotUTF8TxtFileError,
)
from src.contexts.knowledge.application.ports.file_storage_port import FileNotFoundError
from src.contexts.knowledge.application.ports.knowledge_repo import (
    CantCreateFileThatAlreadyExistsError,
    ChunkIdsAreNotUniqueError,
    ChunkNotFoundError,
    FileDoesNotExistError,
    FileTypeNotSupportedError,
    InvalidDatabaseStateError,
    NoChunksExistForThisFileIDErrror,
)
from src.contexts.knowledge.application.ports.vector_store_port import (
    FileIdsToIncludeMustNotBeEmptyError,
    InvalidEmbeddingDimension,
    NoSnippetsForPassedFileIdsExistError,
)
from src.contexts.knowledge.application.ports.vector_store_port import (
    NotFoundError as VectorStoreNotFoundError,
)
from src.interface.http.mappers_data_and_exceptions.all_handlers import (
    register_all_handlers,
)

PORT_ERRORS: tuple[type[BaseException], ...] = (
    ChatNotFoundError,
    ConversationNotFoundError,
    TemporaryConvRepoError,
    CgptNotFoundError,
    DefaultCGPTRetreiverError,
    ErrorWhileCallingAPI,
    NoAssistantResponse,
    ChatCgptPermissionError,
    CgptNotFoundQueryError,
    QueryError,
    MappingError,
    CgptNotFound,
    EmptyListToCheckPassedError,
    UserHasNoPermissionForCgptOrTheyDontExist,
    EmbeddingProviderError,
    NotUTF8TxtFileError,
    FileNotFoundError,
    CantCreateFileThatAlreadyExistsError,
    ChunkIdsAreNotUniqueError,
    ChunkNotFoundError,
    FileDoesNotExistError,
    FileTypeNotSupportedError,
    InvalidDatabaseStateError,
    NoChunksExistForThisFileIDErrror,
    FileIdsToIncludeMustNotBeEmptyError,
    InvalidEmbeddingDimension,
    NoSnippetsForPassedFileIdsExistError,
    VectorStoreNotFoundError,
)


def _registered_exception_types(app: FastAPI) -> Iterable[type[BaseException]]:
    return (
        exception_type
        for exception_type in app.exception_handlers
        if isinstance(exception_type, type)
        and issubclass(exception_type, BaseException)
    )


@pytest.mark.parametrize("port_error", PORT_ERRORS)
def test_every_port_error_has_a_registered_http_handler(
    port_error: type[BaseException],
) -> None:
    app = FastAPI()
    register_all_handlers(app)

    assert any(
        issubclass(port_error, registered_error)
        for registered_error in _registered_exception_types(app)
    )
