# 20. testing the backend

Date: 2025-11-21

## Status

OPEN

## Context

Integrating tests into the software development process is an established process with many benefits.  The downsides of initially more time investment quickly pay off and a net plus is reached fast. Other benefits like direct feedback if something accidentally was broken, tests working as documentation and so on not even included.

Our hexagonal architecture is also made for easy testing, with the possibility of faking ones own adapters where needed and other benefits.   

We want e2e, unit, contract tests. Some tests are more detail oriented (adapter tests) while other fake some adapter and test the functionality of a layer further up.
In this way, we can create tests on different scopes:  
Testing the functionality of an adapter in detail at the outer layer of our app.   
Due to this we know how it works in detail.   
As such, we can go one layer inward, fake it and test the functionality in this layer with abstractions/fake adapters.

A better test folder structure must als be used! See Alberts notes for stlye considerations and practical constraints (e2e <>> other tests: conftest vs bootstrap)

## Decision

We require tests: 

- e2e tests utilizing a Fastapi test client For all the important use cases 
- service layer tests for every function
- tests for each adapter
- tests for dto mappers -i.e. from port dto to fastapi schema

**If we find a (non-trivial) bug, we MUST write a test that catches it, and then fix it**
In this way we know that this edge case or behaviour is checked by our test and will be checked by our tests.

*NON FINAL VERSION OF DOCUMENT*

## Consequences

What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.
