# Format of bootstrap.py

Date: 2025-08-04

## Status

OPEN    

## Context

We need a module where we define all the dependencies that we construct ourselves. This module should take into account either a settings.py for variables like the db url, or take these as parameters and then have another module where we import those and pass the values that we want as parameters and import form there (deps.py)

I want to have typing hints and the ability to use type checkers/linters.
Therefore, just using a dictionary export from a bootstrap function does not work.
What works is having typed functions that take as parameters things like db urls and co in bootstrap.py and importing them in a deps.py where we fill in the values that we need and from where we import them into our app.    
To do everything in one (or additionally with a settings module), we can create a bootstrap function that sets up all the dependencies and returns an object tha contains all the dependencies. 


## Decision
Using the following pattern, running the bootstrap function only once at start up to make sure that the start_mappers function is not running more than once.
We utilize a DependencieContainer object 
```bootstrap.py
@dataclass(frozen=True)
class DependenciesContainer: #Use the Port/Protocol here, not the adapter type!
    session_factory: sessionmaker[Session]
    uow_factory: (() -> UOWPort) #Use the Port/Protocol here, not the adapter type!
    pricing: PricingPort

def enable_sqlite_fk(engine: Engine) -> None:
    if engine.url.get_backend_name() != "sqlite":
        return
    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

def bootstrap(db_url, create_schema, pricing_base_url) -> Container:

    start_mappers()
    engine = create_engine(db_url)
    enable_sqlite_fk(engine)
    session_factory = SessionLocal
    uow_factory = lambda: SAUnitOfWork(session_factory)
    pricing = HttpPricingClient(pricing_base_url)
    return DepoendeciesContainer(session_factory, uow_factory, pricing)
```

```app.py
deps: DependenciesContainer = bootstrap(
    db_url="sqlite:///./dev.sqlite3",
    create_schema=True,                   # only dev/test
    pricing_base_url="https://pricing.example.test"
)

app = FastAPI(title="Inventory")

# Dependencies (no app.state; capture the container)
def uow_dep() -> UnitOfWork:
    return deps.uow_factory()

@app.post("/products", response_model=ProductOut)
def create_product(payload: ProductIn, uow: UnitOfWork = Depends(uow_dep)):
```