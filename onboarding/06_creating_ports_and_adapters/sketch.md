I do want this more in a constructed tutorial way:

So not when what has to be done, but as an introduction to learning the skill to write ports and adapters.

So a follow along/ "tutorial-exercise" -kind of.

Where there are code snippets which need to be completed.

I think about doing it either like this:

using a ipynb which contains all the relevant classes and modules snippets.

At the start we have the Port already defined. 

Then the task for the one onboarded is to write an adapter.



Then there is a cell where the adapter is input and tests are run to confirm:

The functionality that is expected is provided, the errors that are expected are thrown.



----
General to-do per new Port/adapter combo:

### prerequisites new adapter for existing Port:
WIRING
- orchestration function which depend on this Port(or Factory of this Port) exist
- endpoints call orchestration functions with correct parameters - including Port/Port/factory
- dependencies container class has an attribute which is typed as this Port factory/ Port factory factory
- endpoints calling the orchestration function Depend on this dependenciescontainer attribute
(due to how Fastapi depends work, we need the the dependenciescontainer attribute to be  Factory[Factory[Port]] if the orchestration function needs the type Factory[Port])
- in the bootstrap function, the adapter is created (and maybe also a factory (or factory factory)) and used in the returned dependencies container
- if the adapters init needs access to env variables, the bootstrap function takes those as parameter, and in composition.py, require_env() is used to fetch the needed env variable to pass it to the bootstrap() function

MAPPERS INTERFACE
- An exception handler module for this Port is created which maps the Port errors to http errors

MAPPERS APPLICATION
- If applicable, there is a mapper which maps between DTOs and domain data classes

TESTING
- A unit test for the adapter exists which checks functionality incl. custom errors be thrown correctly
- for orchestration layer tests, either the adapter is used (created in conftest) or a fake Adapter was created in the folder `backend/tests/fake_adapters` and used instead
- for e2e integration tests, the previous adapter is used -except if it utilizes a costing external api, where now a fake adapter is used that exists in `backend/tests/fake_adapters`

### Writing a new Port
First determin: is the functionality best fit inside a port or does it belong to the domain?
1. Best fit for a port (external api, providing non-domain-specific functionality) and not for a domain function
2. Create functions & errors, function names must best explain the functionality by themselves and be rather long and explainy: `get_chunks_assert_all_unique_and_exist`, add via comments which errors should be thrown by  a function if not self explanatory
3. If a function returns more than atomic types, create DTO dataclasses for function returns (and parameters if atomic types are not feasible). If there is a corresponding datastructure in the domain, create a mapper function for translation

### Addendum
state based vs non state-based adapters
orm based db - extra is needed

notebook one:
Port is defined, there is already an existing adapter
-> we therefore already have:
The dependenciescontainer already has an attribute of this port type, endpoints and orchestration and every consumer is already correctly wired up with this.
Tests are either already configured with this adapter or a Fake adapter is already created

