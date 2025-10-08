# interface/http/deps.py
from __future__ import annotations #Reference future Types without quotation marks

from src.bootstrap import bootstrap, DependenciesContainer

# Compose ONCE for this process (choose env-specific URL here)
deps: DependenciesContainer = bootstrap(
    db_url="sqlite:///./dev.db",
    create_schema=True,  # dev/test only
)
