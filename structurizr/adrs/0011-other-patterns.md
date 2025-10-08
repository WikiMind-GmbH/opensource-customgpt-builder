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


### OPEN: CQRS & Interface btw http and app
What datatypes to return, where to translate from Domain models to pydantic schema objects?
In http, or deconstruct in app and construct http pydantic in http layer

However, if we use the CQRS pattern, we will probably not have this problem.
Why this pattern is good, is explained in ch12 of cosmic python / architecture patterns with python

## Consequences

This must be reevaluated in the future and better adrs will be created containing all the information