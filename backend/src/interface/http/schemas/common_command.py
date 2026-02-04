from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class CommandResult(BaseModel):
    status: Literal["succeeded"] = "succeeded"
    command_id: str | None = None
    resource_id: str | None = None
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str | None = None
