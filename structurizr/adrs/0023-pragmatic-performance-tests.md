# 23. pragmatic performance tests

Date: 2025-12-05

## Status

Accepted

## Context

Running local tests on our dev machine can only test the basic functionality. However, to test how and if the app will later work as intended for the client when run on our server, this is not enough -we need performance tests for that, which test how our app can handle concurrent requests and edge cases of data sizes.

Due to balancing our time, we want to do this in a minimalistic way only - utilizing pytest.

We can run these test on a vm/server with the same specs as our prod environment.    
In the case of this project, we do not have a seperate prod and staging environment.   
As such, we can simply test it on albert-test.wikinind.de and run the performance tests there. We can simply ssh into it and utilize our makefile to run the tests.   

Additionally, these tests can be a requirement for code to transition from staging to prod.


## Decision

We simply test it on albert-test.wikinind.de and run the performance tests there.    
We ssh into it and utilize our makefile to run the tests. The tests do run in our docker container anyways, so we profit off this previous design decision - (more or less) same virtual environment in prod and dev.

The tests must test both things:
- concurrent requests
- edge cases of datastructure size (i.e. large files/ many files)
The success of both can be evaluated with absolute response time or variability of response time.

## Consequences

It becomes easier to feel confident about the code working in production and bugs or bad optimization can be caught earlier, before being manually tested and used in prod.

The downside is more time needed to write tests. But with the pragmatic, minimalistic solution we propose here, the benefit is definetly worth the cost.