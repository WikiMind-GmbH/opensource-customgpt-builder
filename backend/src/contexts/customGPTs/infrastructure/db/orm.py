# adapters/orm.py
from datetime import datetime, timezone
from sqlalchemy import (
    Table, Column, String, DateTime, MetaData
)
from sqlalchemy.orm import registry

from src.contexts.customGPTs.domain.models import CustomGPT 

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
id: str
name: str
instruction: str
description: str | None = None
custom_gpts = Table(
    "custom_gpts", metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable= False),
    Column("instructions", String, nullable=True),
    Column("description", String, nullable=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False),
)

def start_mappers() -> None:
    mapper_registry.map_imperatively(
        CustomGPT,
        custom_gpts,
    )