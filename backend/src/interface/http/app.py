from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_spanning_helpers import require_env
from src.interface.http.mappers_data_and_exceptions.all_handlers import (
    register_all_handlers,
)
from src.interface.http.routes.chat.chat_commands import chat_commands_router
from src.interface.http.routes.chat.chat_queries import chat_queries_router
from src.interface.http.routes.customGPTs.customGPT_commands import (
    customgpt_commands_router,
)
from src.interface.http.routes.customGPTs.customGPT_queries import (
    customgpt_queries_router,
)

DEBUG_MODE: bool = require_env("DEBUG_MODE").lower() == "true"
if DEBUG_MODE:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))  # Debugger listens on port 5678


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(root_path="/api", lifespan=lifespan)

app.include_router(chat_commands_router)
app.include_router(chat_queries_router)
app.include_router(customgpt_commands_router)
app.include_router(customgpt_queries_router)
# include knowledge routers

register_all_handlers(app)
# ToDo: add other exception handlers
origins = ["https://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
