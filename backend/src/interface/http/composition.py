# from __future__ import annotations #Reference future Types without quotation marks

from backend_spanning_helpers import require_env
from src.bootstrap import DependenciesContainer, bootstrap

# Compose ONCE for this process (choose env-specific URL here)
dependencies_container: DependenciesContainer = bootstrap(
    db_url_chat=require_env("DB_URL_CHAT"),
    db_url_cgpt=require_env("DB_URL_CGPT"),
    db_url_knowledge=require_env("DB_URL_KNOWLEDGE"),
    model_name=require_env("MODEL_NAME"),
    create_schema=require_env("CREATE_SCHEMA").lower() == "true",  # dev/test only
    embedding_model=require_env("EMBEDDING_MODEL"),
    embedding_dimension=int(require_env("EMBEDDING_DIMENSION")),
    db_url_vectorstore=require_env("QDRANT_URL"),
)
