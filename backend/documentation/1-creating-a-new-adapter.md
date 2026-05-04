# Implement new adapter of existing Port for same context
## Preperation
- create new feature-branch from dev
- Find the port (do not change it)
- Read the Protocol methods, DTOs, and port errors
- Create a new module for the adapter. Name of module and Adapter-class best references Port name and module: (`embedding_generator_port` -> `openai_embedding_generator_adapter`)  (context/infrastructure/adapters)
## Write the module code
- Write your adapter module code: think of: i)Map to/from contract DTOs ii) Raise port-defined errors where applicable
## Run unit/integration tests
Search for existing tests that utilize the other adapter of the Port -Utilize the symbol/test search for that and look for results in tests folders
- copy these tests and make the copies run with the new adapter.
- check the readme in the test folder on how to run tests with make targets
## Bootstrap and run run e2e tests with new adapter
- Wire the new adapter in bootstrap (bootstrap.py, composition.py) and run the e2e tests (tests/test_rest_api_use_cases)
## Check quality gates
- Run all tests, linter, type checker - for linting and testing, use the make targets, type checker is in vscode ui
- Check quality gates adr for other necessities to be able to merge into dev from a feature branch and assure your branch fulfills them
# Merge dev into your branch, then create merge request
- If everything is done: merge the current version of dev into your branch and resolve conflicts 
- assure the requirements of the previous section are still fulfilled
- create merge request into dev