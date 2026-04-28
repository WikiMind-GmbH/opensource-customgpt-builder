# Implment adapter for same context
0. create new feature-branch from dev
1. Find the port (do not change it)
2. Read the Protocol methods, DTOs, and port errors
3. Create a new module for the adapter. Name of module and class best references Port: (`embedding_generator_port` -> `openai_embedding_generator_adapter`)  (context/infrastructure/adapters)
4. Map to/from contract DTOs
5. Raise port-defined errors where applicable
6. Write/extend contract and concrete adapter tests and assure they pass (tests/tests/unit/. or tests/tests/integration)
7. check for other test that have this Port as a dependency -e.g. service layer functions (tests/tests/unit/${CONTEXT}/...) and change the fixtures to use your new adapter
8. Wire the adapter in bootstrap (bootstrap.py, composition.py) and run the e2e tests (tests/test_rest_api_use_cases)
9. Run all tests, linter, type checker
10. Check quality gates adr for other necessities to be able to merge into dev from a feature branch
11. If everything is done: merge the current version of dev into your branch, resolve conflicts and run again: tests, linters, type checker. If still everything fine: create merge request into dev