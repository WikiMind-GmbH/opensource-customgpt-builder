from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.contexts.chat.application.ports.customgpt_instructions_retreiver import CgptNotFoundError, DefaultCGPTRetreiverError


def register_query_exception_handlers_cgpt_instruction_retreiver_port(app: FastAPI) -> None:
    @app.exception_handler(CgptNotFoundError)
    async def _not_found(_, exc: CgptNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"Conversation not found: {getattr(exc, 'args', [''])[0]}"
            },
        )
    @app.exception_handler(DefaultCGPTRetreiverError)
    async def _tbd(_, exc: DefaultCGPTRetreiverError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "An unspecified error happened when retreiving chat data"
            },
        )