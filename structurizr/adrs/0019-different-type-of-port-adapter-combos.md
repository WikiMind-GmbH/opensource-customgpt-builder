# 19. Different type of Port Adapter combos

Date: 2025-11-21

## Status

Accepted

Supercedes [Cross context vs in context adapters](0008-cross-context-vs-in-contexat-adapters.md)

## Context

Glossar:
*Context* as in the DDD meaning
*Ports* as in hexagonal Ports

### We have four different type of Port <> Adapter Combos
 
#### Ports used in the service layer: 

1. Ports whose adapter is expected to be implemented in the same context by the db layer, i.e. repos and uows
2. Ports whose adapter is expected to be implemented in the same context not in the db layer, e.g for interfacing with an external api, like the openai Adapter implementing the LlmPort
3. Ports whose adapter is expected to be implemented by another same context

#### Ports used directly in the http layer

4. The queries skip the service layer and directly interact with our db. As such they are directly used in the endpoints, utilizing the session factory.

### In depth
#### 3. Ports whose adapter is expected to be implemented by another same context
Here, we still have the following solution that is only practical for single-few consumer Adapters and a violation of the dependenvy inversion principle. Therefore we do not have to have 2 Ports per cross-context call.  

As of now: The consumer context defines a Port that it expects to be implemented. The provider implements the Port. This creates a dependency of the provider on the consumer.   
The alternative: 
Provider has an inbound port, Consumer has an outbound port, Integration adapter connects the two.
>Now we add a third piece in an integration / anti-corruption layer (or just a technical module that’s allowed to depend on both):
See [here](https://chatgpt.com/s/t_6920846a63c08191b3dc198e7307f1e9) 

## Decision

Point three is our weak point for later scaling.   
However, due to the scope of our project not changing in the forseeable future, and the current solution working rather well for this scope, we will stick with it for now and concentrate on other problematic areas first.

The cleaner way with one port per consumer and provider plus one adapter for wiring should be implemented more easily without much refactoring and should be considered.
A message bus also fulfills a different role.    
Best case would be to combine both: cleaner cross context Port<>Adapter structure as described above PLUS a message bus, as the both fulfill different roles.   [See here](https://chatgpt.com/s/t_692083aa6130819194f1eeef86effa79)

However, we will test both alternatives in a toy project: The more complicated two ports version AND the message bus architecture.

## Consequences

We will have a lower structural overhead for now
