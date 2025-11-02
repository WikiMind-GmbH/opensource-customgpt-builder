# Other architecture patterns
Date: 2025-08-04

## Status

OPEN    

## Context

Patterns that I have not yet finely sorted and put into their own adr will find its place here

## Decision

### Atomic types as service function parameters
Service layer functions will take only atomic types -this is due to decoupling.
See chapter 5 cosmic python / architecture patterns with python book
Open question: what is with the return type, can this be different
Personal take: convoluted types are not really readable, like: `tuple[str|None, List[tuple[Role, str]]]` Returning something else then such a thing might be prettier.

#### update
What about DTOs?

### OPEN: CQRS & Interface btw http and app
What datatypes to return, where to translate from Domain models to pydantic schema objects?
In http, or deconstruct in app and construct http pydantic in http layer

However, if we use the CQRS pattern, we will probably not have this problem.
Why this pattern is good, is explained in ch12 of cosmic python / architecture patterns with python

#### update
Using seperate query module, we should only really need to write dtos for these, posts should only get as return simple types, or otherwise "reroutes" to the queries.

As such, no need for mappers outside of exception handlers and queries should be needed
-> must hold the requrement that service funcions must return simple types somewhere, and think of sop for service functions necessitating more complex return types (DTOs in app layer, )

For now, app layer DTOs of queries will be used either directly or with a minimal wrapper for later complications 

### Exception ownership and structure

https://chatgpt.com/s/t_68f9763ba9bc819182481f31737a043e

### OPEN: naming conventions endpoints
There are conventions about how the names and syntax/structure of endpoint urls related to expected behaviour. As of now, the names are chosen freely and no structure is held up between getters and setters of the same object type for example.

We should, for the sake of a readable api, read and implement these conventions.
## Consequences

This must be reevaluated in the future and better adrs will be created containing all the information