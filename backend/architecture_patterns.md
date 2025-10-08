# Current state of architecture patterns


## Motivation: Unclear patterns often lead to ball of mud:
ToDo: Explain ball of mud, and how not working with clear architecture patterns lead to it + check redundancy with next section

## Background
### Domain driven design


A domain service represents a business concept or process, whereas a service-layer service represents a use case for your application.


### Ports and adapters


### Unmaintainable architecture: ball of mud vs modular architecture
Components are thightly coupled, not cohesive and have multiple responisbilities:
**MINUS 1**
Changes in one component lead to a cascading effect:
Unrelated but coupled components must be changed
Due to unclear boundaries and architecture: The effected components might be unexpected
vs    
Cohesive components with a single responsibility, which depend lightly on other components by self defined Ports:
Changes in one component have no effect if its adapters still fulfill their contracts (the Ports of the consumer that they implement).
ToDo: Show examples
**MINUS 2**
Unmaintainable code:
Less readable: Unclear responsibilities and coupling necessitate understanding more than just the component we want to change/debug.    
vs   
Cohesive components with a single responsibility, which depend lightly on other components by self defined Ports utilizing their own data types:   
make it easy to read and change/debug them due to clear decoupling: No question what a component is supposed to do and how other components depend on it. We also have to only deal with data types that are native to the layer. 

**MINUS 3**




## Goal: Modules with clear interfaces: consumer defines interface

### "Vertical" seperation: Bounded context
Bounded contexts with Ports& adapters for communication between them
(1)Cohesion, (2)single responsibility
(1)One task should be isolated to one component
(2)-One context should have one single task that it is responsible for, not more
ToDo: better word for task -sub domain? sure: bounded context, but that needs explanation itself.




### "Horizontal" seperation: Three layers & dependency injection
TOP: http layer
MIDDLE: (service & domain) layer
BOTTOM: data layer

MIDDLE layer (service & domain):
does not know anything about the data types of the other layers or their implementation, only its own, self defined ports.

Service layer:
- Actual adapers are injected via a bootstrap module that is called in the http layer.
- service layer fulfills uses cases by providing service functions to the http layer, with atomic types and Ports as Parameters. 
- Service layer is called orchestration layer, because it fulfills use cases by orchestrating taks, utilizing domain model functions and the functions of the injected adapters which fulfill its Ports.
- Domain models model the buisness use cases. ToDo: Unclear where the boundaries are -some buisness use cases need adapters, like returning a 

TOP: http layer


### Bootstrapping

We need to inject adapters for the ports that the service layer functions expect.
This is done in the following way.  
we have for a port of one component at least one other component which defines an adapter that implements this Port.

Now, oujr service layer functions that have a Port as a parameter need to be passed an adapter which implements this port. 

We now need to connect our adapters that are defined in some component to the service layer function calls in our http layer.   

Due to decoupling and modularity, we do not want to bake these binds into our http layer directly.

Therefore we have one more layer of abstraction: Bootstrapping, where everything gets wired up.

We have a bootstrap object that we import into our http layer. The http layer only knows that it contains adapters of these ports, or factories for these adapters, not the exact adapters. So the http layer is also independent of implementation details.

In the http layer, we wire everything -we use fastapi dependencies to inject the adapter factories provided by the bootstrap object into the endpoints. The endpoints then pass the adapters to the service layer functions that have the corresponding ports as parameters.

Then we have the bootstrap module which initilizes (factories of) the adapters and sets up everything -like creating a sessionfactory with all the mappings and the correct db url and then creating the UoWs with this sessionfactory.
And makes it available to the http layer via the bootstrap object

Then, by importing






-> Ports and Adapters, 