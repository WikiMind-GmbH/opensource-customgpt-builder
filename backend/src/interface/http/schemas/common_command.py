from datetime import datetime
from typing import Literal

from pydantic import Field, BaseModel


class CommandResult(BaseModel):
    status: Literal["succeeded"] = "succeeded"
    command_id: str | None = None
    resource_id: str | None = None
    at: datetime = Field(default_factory=datetime.utcnow)
    message: str | None = None