# 28. domain invariants with private attributes and invariant save setter functions

Date: 2026-04-10

We want to have a way to assure that certain domain invariants are held.

One way to guarantee some invariants, is that domain model objects properties can not directly be changed.
Rather, 
1) the properties are marked as private with the underscore convention `_private_attribure`. This is also supported by intellisense. So if you try to chanage it directly, pylance will mark this as an error. Meaning: Correctly following our quality gates, you can not commit code where pylance shows errors. Thus, this is more than a convention, it is a requirement in our codebase, making it impossible to set private attributes.
2) Utilizing `@property `/ getter functions
3) utilizuing setter functions, checks if invariants are violated. If so: throw domainInvariant error, change nothing. Otherwise: compute correctly how the properties have to be set/changed. The parameter of the function must not necessarily be used directly. It is possible to only compute values which the properties will be set to based on that.

## Status

>Accepted

## Created by

>List all contributors who have meaningfully edited this ADR.
Version history in Git provides the authoritative change log.

## Decision Maker

>The person responsible for approving this ADR and moving it from OPEN/PROPOSED to ACCEPTED.

>This should be the person accountable for software architecture decisions.
Only this person may mark the ADR as ACCEPTED.



## Scope

Backend domain layer




## Context

Describe:

* The problem or need motivating this decision
* Relevant technical, organizational, or business constraints
* Assumptions made at the time of writing
* Any background information necessary to understand the trade-offs

This section should make it clear *why* a decision is required.



## Alternatives Considered

>List the viable alternatives that were evaluated.

For each alternative, briefly describe:

* The approach
* Its advantages
* Its disadvantages
* Why it was not chosen (if applicable)

If the decision was not a simple this-or-that choice, describe the key dimensions and trade-offs that were considered.



## Decision

Describe the chosen solution clearly and unambiguously.

This section should state:

* What will be implemented
* Any key design constraints or rules introduced
* Any standards, technologies, or patterns that must be followed

The decision should be actionable and leave minimal room for interpretation.



## Consequences

Describe the impact of this decision, including:

* Benefits introduced
* Trade-offs accepted
* New limitations or constraints
* Risks and how they may be mitigated
* Follow-up work required (if any)

Be explicit about what becomes easier and what becomes harder as a result.
