from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_general_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # return PlainTextResponse(str(exc), status_code=400)
        # pick just the first error
        error = exc.errors()[0]
        # error["loc"] is like ["body","custom_gpt_description"]
        field = ".".join(str(x) for x in error["loc"][1:])
        msg = f"{field}: {error['msg']}"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": msg},
        )
