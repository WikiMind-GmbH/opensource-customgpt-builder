# Testing
This documents the structure of the test folders: where each category of test is to be found and written.   
Utilize the make targets to run them.

The guidelines for writing tests can be found in the adrs.


# There are four different folders:
## test_external_api_adapters
... is for testing adapters utilizing external - maybe *paid* -  apis. Thus it is extra - we do not want to test it every time to save money
## tests_perf_locust
...  is for performance testing our api endpoints
## test_rest_api_use_cases 
... are the light e2e tests
## `tests``
...  are the rest of the tests, which do not fit any of the categories listed above - unit tests, contract and integration tests

# Other
## Pytest-benchmark
Pytest benchmark performance tests of `components`(adapters/service functions/..) are placed alongside the functional tests of these components. So the can be found in any of the tree non-locust test folders. 
The are marked with 
```
@pytest.mark.performance
@pytest.mark.benchmark(
```
And the make targets are set in a way such that they are excluded per default. See the makefile for more info