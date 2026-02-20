# 24. Reason Required When Ignoring Type Checker Warnings

## Status

OPEN


## Created by

Albert Sandritter


## Decision Maker

(To be filled)


## Scope

This ADR applies to all Python code in this repository that is checked with our static type checker (e.g., Pyright/Pylance).

It governs how and when type checker warnings may be ignored.


## Context

We have established the rule that the type checker should not report unresolved problems in our codebase.
We already configure it to ignore issues originating from untyped third-party libraries.

However, static type checkers are inherently limited. They analyze code syntactically and structurally, but they do not always have full semantic context.

In some cases, the type checker reports warnings that are technically correct from a syntactic perspective, but semantically incorrect in our actual program behavior.

Example:
When registering exception handlers via decorators, the type checker may report that the handler function is unused. In reality, the function is used indirectly because the decorator performs registration as a side effect. The tool cannot infer this mechanism.

In such cases:

* The warning is not indicating a real defect.
* Refactoring may be possible, but sometimes there is no clean or idiomatic alternative.
* Attempting to “satisfy” the type checker may reduce clarity rather than improve correctness.

The type checker is a means to improve code quality — not an end in itself.

We therefore need clear criteria for deciding:

* When a warning must be resolved
* When it is acceptable to explicitly ignore it
* How such ignores must be documented
* How they are revisited during refactoring

Without a process, we risk either:

* Over-engineering solutions to non-problems, or
* Accumulating careless ignore statements that hide real issues.


## Alternatives Considered

### 1. Never ignore any warning

Strictly enforce zero ignores and require refactoring in all cases.

**Pros**

* Maximum theoretical strictness
* No hidden warnings

**Cons**

* Can lead to convoluted or unnatural code
* Encourages workarounds that reduce readability
* Does not acknowledge tooling limitations


### 2. Allow arbitrary ignores without documentation

Developers may ignore warnings at their discretion.

**Pros**

* Fast
* Low friction

**Cons**

* High risk of masking real problems
* No accountability
* Technical debt accumulates silently


### 3. Allow controlled, documented, line-specific ignores (Proposed)

Allow ignoring warnings under strict criteria and documentation requirements.

**Pros**

* Balances pragmatism and discipline
* Preserves code clarity
* Maintains accountability
* Keeps ignores visible and reviewable

**Cons**

* Requires discipline and periodic review
* Adds minor overhead when ignoring a warning


## Decision

We adopt a controlled and documented approach to ignoring type checker warnings.

A warning may only be ignored if:

* The type checker is misidentifying a problem that is not semantically present.
* The relevant information is explicit in the code but not inferable by the tool.
* A reasonable effort has been made to find a clean and idiomatic solution.
* No better solution was found within reasonable time.

If the decision is made to ignore a warning, the following rules apply:

1. The ignore must apply to exactly one error type on exactly one line.

   * Never ignore globally.
   * Never ignore multiple error types at once.

2. A short inline explanation must be added next to the ignore statement explaining why the warning is intentionally suppressed.

3. During refactoring sessions, all instances of
   `# pyright: ignore[ErrorType]`
   must be reviewed and briefly re-evaluated.

The burden of justification lies with the developer introducing the ignore.


## Consequences

### Positive

* Prevents unnecessary refactoring driven solely by tooling limitations.
* Maintains readability and architectural clarity.
* Keeps ignores explicit and reviewable.
* Encourages conscious, documented decisions.

### Negative / Risks

* Ignored warnings may remain in the code even after better solutions become available.
* Without regular review, justified ignores may turn into unnoticed technical debt.
* **We do not have a regular review policy in place as of now!**
* Refactoring opportunities may be missed if ignore statements are not revisited.

To mitigate these risks:

* Ignore statements must always include an explanation.
* Refactoring efforts must explicitly review existing ignore directives.

#### When ignoring at badly typed libraries boundaries
Using ignores where it is mostly lazily pragmatic at untyped library boundaries:
one should rather Seal Unknown/Any at the boundary:
cast once right after you call the framework/untyped lib
then keep everything inside your app strongly typed