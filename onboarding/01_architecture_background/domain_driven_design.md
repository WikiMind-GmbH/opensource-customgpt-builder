# Introduction to Domain-Driven Design

## Purpose

This document introduces the core ideas of **Domain-Driven Design**, usually abbreviated as **DDD**.

It is intended as an onboarding document for developers who are new to DDD or who have only seen parts of it before. It does not cover every advanced DDD concept. Instead, it focuses on the concepts we need early when working in a modular backend architecture.

A separate document should introduce **Hexagonal Architecture** in more detail. This document only references it where necessary to explain how DDD boundaries connect to the rest of the architecture.

---

## What Is Domain-Driven Design?

Domain-Driven Design is an approach to software design that puts the **business domain** at the center of the system.

Instead of organizing code mainly around technical concerns like databases, HTTP APIs, frameworks, or external services, DDD encourages us to organize software around the real-world concepts and rules that the system is meant to support.

In simple terms:

```text
The most important part of the software is the business problem it solves.
```

DDD helps us express that business problem clearly in code.

---

## Why DDD Matters

Many systems start simple but become harder to change over time.

Common problems include:

```text
business logic scattered across controllers, database models, and utility functions
unclear ownership of concepts
different parts of the system using the same word with different meanings
technical details influencing the shape of business logic
changes in one area causing unexpected changes in another area
tests that require too much infrastructure setup
```

DDD helps reduce these problems by encouraging clear boundaries, explicit models, and a shared language.

The goal is not to create more abstraction for its own sake.

The goal is to make the system easier to understand, change, test, and evolve.

---

## The Domain

The **domain** is the problem space the software is about.

For an e-commerce system, the domain might include:

```text
products
carts
orders
payments
shipments
returns
discounts
```

For a banking system, the domain might include:

```text
accounts
transfers
balances
transactions
limits
fraud checks
```

For a chat or AI assistant system, the domain might include:

```text
conversations
messages
prompts
documents
retrieved evidence
generated responses
```

The domain is not the database.
The domain is not the API framework.
The domain is not the UI.

The domain is the set of concepts, rules, workflows, and language that make the software useful.

---

## Subdomains

A **subdomain** is a smaller part of the overall domain.

It describes a business capability or area of responsibility.

For example, in an e-commerce system, possible subdomains could be:

```text
Ordering
Payment
Shipping
Catalog
Customer Support
```

Each subdomain has its own concepts, language, and rules.

For example, “customer” might not mean exactly the same thing everywhere:

```text
Ordering: a customer places an order
Billing: a customer is a billable account
Support: a customer is someone requesting help
```

DDD helps us avoid forcing all of these meanings into one global model.

---

## Bounded Contexts

A **bounded context** is a boundary within which a domain model and language are consistent.

Inside one bounded context, terms should have one clear meaning.

Outside that context, the same term may mean something different.

Example:

```text
Ordering context:
  Order means a customer purchase with items, prices, and order status.

Shipping context:
  Order may mean a shipment request with delivery address and tracking state.

Billing context:
  Order may mean something that must be invoiced or paid.
```

These models may be related, but they are not necessarily the same model.

The key rule is:

```text
Each bounded context owns its own model and language.
```

This avoids one large model that tries to satisfy every part of the system and becomes unclear over time.

---

## Our Use of Subdomains and Bounded Contexts

In this architecture, we intentionally use a simple first-iteration rule:

```text
Each subdomain is implemented as exactly one bounded context.
```

That means we currently align business capabilities directly with code boundaries.

Example shape:

```text
Subdomain A -> Bounded Context A
Subdomain B -> Bounded Context B
Subdomain C -> Bounded Context C
```

This is a deliberate design choice.

It gives us:

```text
clear ownership
simple onboarding
easy navigation in the codebase
business-aligned module boundaries
a good foundation for later refinement
```

This rule does not mean that subdomains and bounded contexts are always the same thing in DDD theory.

In larger or more mature systems, one subdomain may be split into multiple bounded contexts, or one bounded context may cover parts of multiple subdomains. However, for our current architecture, the one-to-one mapping is the intended starting point.

---

## Ubiquitous Language

The **ubiquitous language** is the shared language used by developers and domain experts inside a bounded context.

The code should use this language.

If the business says:

```text
An order can be cancelled until it has shipped.
```

The code should look similar:

```python
order.cancel()
```

and not like:

```python
order.update_status("C")
```

Good naming makes the code easier to discuss with non-technical stakeholders and easier for developers to understand.

The ubiquitous language is scoped to a bounded context.

That means the same word can have a different meaning in another context. This is not automatically a problem. It becomes a problem only when we ignore the context boundary and pretend the word must mean the same thing everywhere.

---

## Domain Model

A **domain model** is the code representation of the domain inside a bounded context.

It contains the important concepts and rules of that context.

A good domain model does not only store data. It also expresses behavior.

For example, an anemic model might look like this:

```python
@dataclass
class Order:
    status: str
    items: list[OrderItem]
```

This stores order data, but it does not explain what an order can do or what rules apply.

A richer domain model might express behavior directly:

```python
@dataclass
class Order:
    status: OrderStatus
    items: list[OrderItem]

    def cancel(self) -> None:
        if self.status is OrderStatus.SHIPPED:
            raise OrderAlreadyShippedError()

        self.status = OrderStatus.CANCELLED
```

Now the model contains a business rule:

```text
A shipped order cannot be cancelled.
```

This rule belongs in the domain because it is a business invariant, not a technical detail.

---

## Entities

An **entity** is a domain object with identity.

Its identity matters even if some of its attributes change.

Example:

```python
@dataclass
class Customer:
    id: CustomerId
    email: EmailAddress
    name: str
```

A customer may change their email address or name, but they are still the same customer if the identity remains the same.

Entities are useful when the lifecycle of a thing matters.

Common examples:

```text
customer
order
invoice
conversation
document
account
```

---

## Value Objects

A **value object** is a domain object defined by its value, not by identity.

Example:

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency
```

Two `Money` objects with the same amount and currency are usually considered equal.

Value objects are useful for making implicit rules explicit.

Instead of this:

```python
price: Decimal
currency: str
```

Prefer this:

```python
price: Money
```

The value object can enforce rules:

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise NegativeMoneyAmountError()
```

Good value objects make invalid states harder or impossible to represent.

Common examples:

```text
money
email address
date range
percentage
address
quantity
language code
```

---

## Invariants

An **invariant** is a rule that must always be true for the domain model.

Examples:

```text
A shipped order cannot be cancelled.
A bank account cannot be overdrawn beyond its limit.
A discount cannot be applied after payment.
A message must belong to a conversation.
```

Invariants should be protected by the domain model.

This is important because boundary validation alone is not enough.

For example, an HTTP request schema may validate that an amount is a number, but the domain must still protect rules like:

```text
The amount must not exceed the account limit.
```

The boundary checks whether the input has the right shape.
The domain checks whether the operation is allowed according to business rules.

---

## Repositories

A **repository** provides access to domain objects.

It hides persistence details from the application and domain model.

Instead of application code using SQL directly, it depends on a repository interface:

```python
class OrderRepository(Protocol):
    def get(self, order_id: OrderId) -> Order: ...

    def save(self, order: Order) -> None: ...
```

A database-backed implementation can use SQLAlchemy, raw SQL, or another persistence technology.

The application code should not need to know which one.

This keeps persistence concerns separate from business logic.

Repositories are closely related to Hexagonal Architecture because they are usually expressed as ports and implemented by infrastructure adapters.

A separate Hexagonal Architecture document should explain this relationship in more detail.

---

## Unit of Work

A **Unit of Work** manages a business transaction.

It usually coordinates repositories and commits or rolls back changes.

Example:

```python
def cancel_order(order_id: OrderId, uow: OrderUnitOfWork) -> None:
    with uow:
        order = uow.orders.get(order_id)
        order.cancel()
        uow.orders.save(order)
        uow.commit()
```

The use case controls the transaction boundary, while the domain model controls the business rule.

This separation is important:

```text
Application layer: When does the transaction start and end?
Domain layer: Is this business operation allowed?
Infrastructure layer: How is this persisted?
```

Like repositories, Unit of Work is commonly implemented using Hexagonal Architecture patterns. The application depends on an abstraction, while infrastructure provides the concrete implementation.

---

## Application Services / Use Cases

An **application service** represents a use case.

It coordinates the work needed to fulfill a user or system action.

Example:

```python
def place_order(
    command: PlaceOrderCommand,
    uow: OrderUnitOfWork,
    payment_port: PaymentPort,
) -> OrderId:
    with uow:
        order = Order.create(
            customer_id=command.customer_id,
            items=command.items,
        )

        payment_port.charge(command.payment)

        uow.orders.save(order)
        uow.commit()

        return order.id
```

The application service coordinates:

```text
loading data
calling domain behavior
using dependencies through abstractions
committing transactions
returning results
```

It should avoid becoming the place where all business rules live.

Business rules that belong to the model should be implemented in the domain model.

---

## DTOs at Boundaries

A **DTO** is a Data Transfer Object.

DTOs are useful when data crosses a boundary:

```text
HTTP request/response boundary
application-to-infrastructure boundary
context-to-context boundary
external API boundary
```

DTOs should represent the contract, not internal implementation details.

Avoid passing these across boundaries where they do not belong:

```text
ORM models
internal domain entities
external SDK objects
database rows
framework-specific request objects
```

A good boundary often looks like this:

```text
Internal model -> mapper -> DTO -> boundary -> mapper -> internal model
```

The mapping may feel like extra work, but it protects the system from accidental coupling.

---

## Context Boundaries and DTOs

Bounded contexts should communicate through explicit boundaries.

They should not freely share internal models.

Avoid this:

```text
Billing context directly imports Order from Ordering context.
```

Prefer this:

```text
Billing context receives a contract DTO from an explicit boundary.
```

This matters because internal models change for internal reasons.

If other contexts depend on those models directly, a local change can become a system-wide refactor.

The general rule is:

```text
Internal models stay inside their owning context.
Data crossing context boundaries uses explicit DTOs.
Mapping happens at the boundary.
```

---

## Commands and Queries

Many systems benefit from separating write use cases from read use cases.

### Commands

Commands change state.

Examples:

```text
Create order
Cancel subscription
Upload document
Send message
Update profile
```

Commands usually go through application services and domain models.

They should enforce business rules and protect invariants.

### Queries

Queries read data.

Examples:

```text
List orders
Get invoice summary
Show conversation history
Search documents
```

Queries often return DTO projections optimized for the caller.

They do not always need to load full domain entities.

This lightweight separation is often enough without introducing a full CQRS or event-sourcing architecture.

---

## Validation

Validation happens at different levels.

### Input Validation

Input validation checks whether incoming data has the right shape.

Example:

```text
email is present
amount is a number
date has valid format
```

This often belongs at the boundary, such as HTTP request validation.

### Domain Validation

Domain validation checks whether something is allowed according to business rules.

Example:

```text
A shipped order cannot be cancelled.
A user cannot access another user's private document.
A payment cannot be captured twice.
```

These rules should live in the domain model or close to the domain model.

The difference is:

```text
Input validation: Is the data structurally valid?
Domain validation: Is this operation meaningful and allowed?
```

---

## Error Handling

Domain errors should express domain meaning.

Good:

```python
class OrderAlreadyShippedError(Exception):
    pass
```

Less good inside the domain:

```python
raise HTTPException(status_code=400)
```

HTTP is a transport concern. The domain should not know about HTTP status codes.

A typical flow is:

```text
Domain raises domain error
Application lets it bubble up
Interface layer translates it into HTTP response, CLI output, etc.
```

This keeps the domain reusable and independent from the delivery mechanism.

---

## Testing DDD Code

DDD-friendly code is usually easier to test because business logic is separated from infrastructure.

Common test types:

### Domain Tests

Test business rules directly.

```python
def test_shipped_order_cannot_be_cancelled() -> None:
    order = shipped_order()

    with pytest.raises(OrderAlreadyShippedError):
        order.cancel()
```

These tests should be fast and require no database.

### Application Service Tests

Test use cases with fake repositories or fake ports.

```python
def test_cancel_order_commits_transaction() -> None:
    uow = FakeOrderUnitOfWork()
    cancel_order(order_id, uow)

    assert uow.committed
```

### Adapter Tests

Test infrastructure implementations separately.

Examples:

```text
SQLAlchemy repository tests
external API adapter tests
file storage adapter tests
```

### Mapper Tests

Test translation between DTOs and internal models.

Mapping code protects boundaries, so it deserves tests when it is non-trivial.

---

## Relationship to Hexagonal Architecture

DDD and Hexagonal Architecture solve different but complementary problems.

DDD helps answer:

```text
How should we model the business domain?
Where are the boundaries between business capabilities?
Which language belongs inside each boundary?
Where should business rules live?
```

Hexagonal Architecture helps answer:

```text
How do we keep business logic independent from frameworks and infrastructure?
How do use cases depend on abstractions instead of concrete implementations?
How do repositories, external APIs, and other technical concerns plug into the application?
```

In short:

```text
DDD defines the domain model and boundaries.
Hexagonal Architecture protects those boundaries technically.
```

This document focuses on DDD.

A separate onboarding document should explain Hexagonal Architecture, including:

```text
ports
adapters
dependency inversion
repository ports
external service ports
adapter implementations
dependency wiring
testing through fake adapters
```

---

## Common Mistakes

### Mistake: Putting all logic in controllers

Controllers should handle transport concerns. They should not own business rules.

Avoid:

```text
HTTP endpoint validates request, loads database rows, applies business rules, calls external API, commits transaction.
```

Prefer:

```text
HTTP endpoint validates request shape and calls an application use case.
```

---

### Mistake: Treating domain models as database models

A domain model should express business meaning.

A database model should express persistence structure.

Sometimes they look similar, especially in small systems, but they are not the same responsibility.

---

### Mistake: Sharing one model everywhere

A single global model often becomes too large and unclear.

Different contexts may need different models for similar concepts.

---

### Mistake: Using DTOs as domain models

DTOs carry data across boundaries.

They should not become the place where core business behavior lives.

---

### Mistake: Avoiding mapping code at all costs

Mapping feels repetitive, but it is often the price of clean boundaries.

Removing all mapping usually means coupling parts of the system that should remain independent.

---

## Practical Checklist

When adding new functionality, ask:

```text
Which subdomain owns this behavior?
Which bounded context represents that subdomain?
What are the important domain concepts?
What business rules must always be true?
Which terms belong to this context’s ubiquitous language?
Which layer should this code live in?
What data crosses a boundary?
Which DTO represents that boundary contract?
Where does mapping happen?
How can this be tested without real infrastructure?
```

These questions help keep the design intentional.

---

## Summary

Domain-Driven Design is about aligning software with the business domain.

The most important ideas are:

```text
put business concepts at the center
split the domain into subdomains
represent subdomains as bounded contexts in this architecture
use clear domain language in code
keep each bounded context’s model independent
separate domain logic from technical infrastructure
avoid sharing internal models across boundaries
use DTOs and mappers to protect contracts
keep use cases in the application layer
keep business rules in the domain layer
test domain logic without requiring databases or external services
```

DDD is not about making everything more complicated.

It is about managing complexity where the business itself is complex.
