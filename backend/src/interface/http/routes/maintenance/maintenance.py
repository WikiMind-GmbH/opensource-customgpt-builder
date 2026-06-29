from fastapi import APIRouter, Response

from src.bootstrap import DependenciesContainer
from src.interface.http.composition import dependencies_container

maintenance_router = APIRouter(prefix="/maintenance", tags=["Maintenance: Query"])

dependencies_container: DependenciesContainer = dependencies_container


@maintenance_router.get("/healthz", include_in_schema=False)
def healthz() -> Response:
    return Response(status_code=204)
