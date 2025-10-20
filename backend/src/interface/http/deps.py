# interface/http/deps.py
from __future__ import annotations #Reference future Types without quotation marks

from src.bootstrap import bootstrap, DependenciesContainer

# Compose ONCE for this process (choose env-specific URL here)
deps: DependenciesContainer = bootstrap(
    db_url_chat="sqlite:///./dev-chat.db",
    db_url_cgpt="sqlite:///./cgpt-chat.db",
    model_name="gpt-4.1-mini",
    create_schema=True,  # dev/test only
)