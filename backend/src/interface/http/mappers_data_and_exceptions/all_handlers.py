from fastapi import FastAPI

from src.interface.http.mappers_data_and_exceptions.chat.cgpt_instructions_retreiver import (
    register_query_exception_handlers_cgpt_instruction_retreiver_port,
)
from src.interface.http.mappers_data_and_exceptions.chat.chat_queries_classes_and_exceptions import (
    register_query_exception_handlers_queries_port,
)
from src.interface.http.mappers_data_and_exceptions.chat.chat_repo import (
    register_query_exception_handlers_chat_repo_port,
)
from src.interface.http.mappers_data_and_exceptions.chat.llm_port import (
    register_query_exception_handlers_llm_port,
)
from src.interface.http.mappers_data_and_exceptions.customGPTs.cgpt_queries_classes_and_exceptions import (
    register_query_exception_handlers_cgpt_query_port,
)
from src.interface.http.mappers_data_and_exceptions.customGPTs.conversation_port import (
    register_query_exception_handlers_conv_port,
)
from src.interface.http.mappers_data_and_exceptions.knowledge.ports.cgpt_permissions_adapter_exceptions import (
    register_query_exception_handlers_cgpt_permission_port,
)


def register_all_handlers(app: FastAPI):
    register_query_exception_handlers_queries_port(app)
    register_query_exception_handlers_chat_repo_port(app)
    register_query_exception_handlers_cgpt_instruction_retreiver_port(app)
    register_query_exception_handlers_llm_port(app)
    register_query_exception_handlers_cgpt_query_port(app)
    register_query_exception_handlers_conv_port(app)
    # Knowledge Context
    register_query_exception_handlers_cgpt_permission_port(app)
