# Utilizing DTOs in cross-context ports
Date: 2025-08-04

## Status

Superceded by [26. DTOs at boundaries: contract data must be independent from internal models](0026-dtos-at-boundaries-contract-data-must-be-independent-from-internal-models.md)

## Context
Our contexts each have their own domain models and we want to make sure that the contexts are decoupled from each other.   
If we now have cross context communication via Ports of Context `A` and Adapter implementing this Port in context `B`, we must pay close attention to how we define this interface to not create coupling.   
A)
We might be tempted to use domain models of `A` in the Port. But that binds the Port to the domain model and that is not advisable because 1) we don't want to have to modify the port(&adapters) every time we change something in the domain model 2) the domain model might contain way more information than we need for our interface 3) We don't want to leak internals of a context to the outside.

Therefore, DTOs and a mapper translating those is a solid and widely used choice.
B)
Additionally, we have the problems of the following kind:       
The adapter of Context B might need to access its db and therefore needs it uow.   
We don't want to have the uow of `B` as a parameter of the Port function of `A`or anything that couples the contexts.   
Therefore we will have the uow and similar dependencies as properties of the adapter (not defined in the port.) and then wire them up in the bootstrap.   
In this way, we have no coupling.


## Decision

We will define DTOs in the Port and utilize those in the Ports functions to pass data.
The context owning the Port with its DTOs will then define a mapper function to translate the DTOs to domain objects.   
If we change the domain model or DTO, we will only have to adjust this mapper function and nothing more

Additionally, we will define per Cross context Port<>Adapter in the Port: DTOs and a mapper function.

## Consequences

