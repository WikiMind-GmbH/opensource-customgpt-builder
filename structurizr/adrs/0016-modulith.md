# 16. Modulith

Date: 2025-11-19

## Status

Accepted

Supercedes [Microservices Architecture](0003-Microservices-architecture-test)
Supercedes [Seperating internal and external endpoints via nginx](0005-Seperating-internal-and-external-endpoints-via-nginx)

## Context
*PLACEHOLDER TEXT*
A previous decision proposed a microservice architecture to achieve modularity, decoupling, and clear bounded contexts.

Our current system is relatively small in scope. We apply Domain-Driven Design (DDD) with a hexagonal (ports & adapters) architecture. All cross-context communication is already modeled via interfaces (ports) with concrete implementations in adapters. This gives us clear boundaries and stable contracts between modules.

## Decision
We will implement the system as a **modulith** (modular monolith) using DDD and hexagonal architecture instead of splitting the system into separate deployable microservices.

## Rationale
- We still get **modularity, decoupling, and clear domain boundaries** via DDD and hexagonal design within a single deployable unit.
- For our **current scope (small project)**, a modulith reduces operational and organizational complexity compared to a microservice landscape.
- We **avoid the overhead** of inter-service **HTTP calls** (latency, serialization, circuit breakers, retries, distributed tracing, etc.), while keeping module boundaries explicit.
- Because all cross-context communication already goes through **ports and adapters**, modules can be **extracted into microservices later** with minimal change: the contracts are stable and well-defined.

## Consequences
- **Pros**
  - Simpler deployment, monitoring, and operations (single application).
  - Lower runtime overhead (no network hops between domain modules).
  - Clear path to future **microservice extraction**, if/when system size and team structure justify it.
  - Consistent DDD & hexagonal patterns across all modules.

- **Cons**
  - No independent deployment per bounded context initially.
  - Some microservice-specific concerns (e.g. per-service scaling, independent tech stacks) are not available until modules are extracted.

