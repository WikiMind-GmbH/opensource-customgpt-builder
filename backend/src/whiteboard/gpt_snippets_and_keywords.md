- Hexagonal (ports&adfapters)
- service layer functions take primitives, not domain models or pydantic model -refrain from other overly complicated ch. 5 of architecture patterns python
- value vs entity objects (equality operator difference -see [chapter 1](https://www.cosmicpython.com/book/chapter_01_domain_model.html#_dataclasses_are_great_for_value_objects))
- TD: A tiny error mapping layer (raise domain/app exceptions → map to HTTP 400/404)


## Open questions that come to mind
- For integration test: Pytest fixtures vs explicit session factory passed to tests
- Where are the tables created? -fastapi lifecyle in general
- [context manager vs yield](https://chatgpt.com/s/t_68d3092f472081919243e1500496fa00)
- How to write tests for external adapters for ports [(i.e. different context has adapter for port)](https://chatgpt.com/s/t_68d30cab2a6c8191b8c7320939c746c5)
- How to write indices for database performance [improvements](https://chatgpt.com/s/t_68d30cab2a6c8191b8c7320939c746c5)
- fastapi app state - what to use it for, pros in contrast to explicitly importing 
## Concept rubber ducking
- Dependency injection via deps, bootstrap
- 


## Solutions for next steps (non-final)

- use lifecycle for start up and shut down logic (not completely)
```.py
With lifespan, your dependency can read from request.app.state to avoid global imports if you want:

from fastapi import Request
from demo.service_layer.ports import UnitOfWork
from demo.adapters.uow import SQLModelUnitOfWork

def provide_uow(request: Request) -> UnitOfWork:
    sf = request.app.state.session_factory
    return SQLModelUnitOfWork(sf)
# This keeps engine/session details out of your route code and localized to composition.
If you want it even more separated, put the wiring in entrypoints/composition.py (as above) and have routes import only provide_uow and the ports/services.
```

- start with create tables manually at startup before moving to alembic
```
# ensure ONDELETE CASCADE works in SQLite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _):
    try:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        pass
```

## Solution final

### DB creation, deps
```
main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import create_engine
from adapters.orm import metadata, start_mappers  # your snippet

DATABASE_URL = "postgresql+psycopg://user:pass@localhost/dbname"

engine = create_engine(DATABASE_URL, future=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mappers()                   # map classes -> tables
    metadata.create_all(engine)       # dev/test only
    try:
        yield
    finally:
        # optional in dev; leave it out if you want data to persist
        # metadata.drop_all(engine)
        pass

app = FastAPI(lifespan=lifespan)
```
### Settings.py
Use a settings module [see](https://chatgpt.com/s/t_68d3023d89ec8191895eda0e0c3bee62)
[blogpost](https://medium.com/@jayanthsarma8/config-management-with-pydantic-base-settings-de22b79fd191)
#### How to adapt this to use deps.py
#### How to adapt this to integrate the new uows etc into the old app.py
Problem:
Conflict with old sqlmodel tables!
Remove conversation and message tabe from legacy code & add table creation for sqlalchemy to table creation of legacy in lifecycle

KEYWORD: `metadata.create_all, from orm import metadata`
### Tests
FastAPI overrides are great for swapping anything (UoW, settings, clients) without changing your app code.
```
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from adapters.orm import metadata, start_mappers

TEST_DB_URL = "sqlite:///:memory:"  # or a real Postgres URL for integration tests

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DB_URL, future=True)
    start_mappers()
    metadata.create_all(engine)
    yield engine
    metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    trans = connection.begin()
    Session = sessionmaker(bind=connection, expire_on_commit=False, future=True)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()

@pytest.fixture
def uow_factory(engine):
    # If your UoW takes a SessionFactory:
    Session = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    def factory():
        from adapters.uow import SQLAlchemyConversationUOW
        return SQLAlchemyConversationUOW(Session)
    return factory

```

```
def test_create_message(uow_factory, db_session):
    uow = uow_factory()
    # use uow/session; schema is already created for the session

```




# Where to continue summary
## DD project layer explanation chat
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from adapters.uow import SAUnitOfWork
from config.db import create_all, session_factory
from service_layer import services
from domain.models import Role, ContentType
from service_layer.ports import UnitOfWork

app = FastAPI(title="Conversations API")

@app.on_event("startup")
def startup():
    create_all()