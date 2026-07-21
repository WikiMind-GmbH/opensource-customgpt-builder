from backend_spanning_helpers import require_env
from src.bootstrap import DependenciesContainer, bootstrap

dependencies_container: DependenciesContainer = bootstrap(
    db_url_chat=require_env("DB_URL_CHAT"),
    db_url_cgpt=require_env("DB_URL_CGPT"),
    db_url_knowledge=require_env("DB_URL_KNOWLEDGE"),
    model_name=require_env("MODEL_NAME"),
    llm_base_url=require_env("LLM_BASE_URL"),
    llm_api_key=require_env("LLM_API_KEY"),
    create_schema=require_env("CREATE_SCHEMA").lower() == "true",
    embedding_model=require_env("EMBEDDING_MODEL"),
    embedding_dimension=int(require_env("EMBEDDING_DIMENSION")),
    db_url_vectorstore=require_env("QDRANT_URL"),
)
