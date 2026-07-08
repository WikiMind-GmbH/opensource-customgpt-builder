# Coding Principles: Linting and Typing

## Purpose

This section explains why we use linting, formatting, and type checking in everyday development.

It focuses on line-by-line coding quality:

```text
Is this code formatted consistently?
Are imports clean?
Are names and types understandable?
Can the editor understand this code?
Can obvious mistakes be found before tests run?
```

This section does not cover architectural principles such as context boundaries, isolation, or responsibility ownership.

---

## Why This Matters

Linting and typing are a first quality filter.

They catch many mistakes before we write or run tests:

```text
wrong imports
unused variables
wrong function arguments
missing attributes
unsafe assumptions about None
wrong return types
unreachable or inconsistent code
formatting noise
```

This makes programming easier because feedback is immediate. The editor can show problems while writing the code, instead of discovering them later through failing tests or manual review.

Tests answer:

```text
Does the behavior work?
```

Linting and typing answer earlier questions:

```text
Is this code even structurally clean?
Do the pieces fit together?
Can other developers understand and refactor it safely?
```

They are not a replacement for tests, but they are an early testing step.

---

## Ruff: Formatting and Linting

Ruff is used to keep Python code consistently formatted and lint-clean.

This removes many small discussions from code review:

```text
import order
unused imports
formatting style
simple lint issues
minor cleanup
```

The benefit is not only prettier code. Consistent formatting makes diffs smaller and reviews easier. Reviewers can focus on the actual change instead of personal formatting preferences.

Run Ruff through the Makefile:

```bash
make ruff
```

For safe automatic fixes:

```bash
make ruff-fix-save
```

Review the diff after automatic fixes.

The Makefile is the preferred developer interface for project commands, so use the make targets instead of long tool-specific commands where possible.

---

## Type Checking: Why We Care

Type checking gives fast feedback about whether code fits together.

Good types make code easier to read because function signatures explain intent:

```python
def get_conversation(conv_id: str) -> Conversation:
    ...
```

This tells the reader what goes in and what comes out without inspecting the whole function.

Bad or overly broad types hide intent:

```python
def get_conversation(conv_id: Any) -> Any:
    ...
```

The type checker is especially useful when refactoring. If a return type changes, or a function needs another parameter, the editor can show affected call sites immediately.

ADR 25 is the main document for typing guidelines. Read it when deciding how specific a type should be, especially when choosing between a precise concrete type and a more generic type like `Callable` or `Any`. Its central rule is to prefer precise, meaningful types when they improve readability and allow stronger checks.

---

## Precise Types Make Code More Maintainable

Prefer types that communicate real intent.

The goal is not to make types abstract. The goal is to make them useful.

For example, if a concrete library type carries important meaning, use it instead of hiding it behind a too-generic type. ADR 25 gives this exact motivation: richer types preserve information, improve readability, and let the type checker enforce stronger guarantees.

A good type should help answer:

```text
What does this function expect?
What does this function return?
What guarantees does the caller have?
What mistakes can the editor catch immediately?
```

---

## Editor Feedback Is Part of the Workflow

The project’s `settings.json` configures strict Pyright/Pylance checking for the backend, enables workspace diagnostics, adds the backend to analysis paths, and configures Ruff as the Python formatter on save. It also reduces noise for some third-party-library typing problems so developers can focus more on problems in our own code.

This means VS Code is not just an editor here. It is part of the development feedback loop.

Use editor warnings seriously. They often show problems before tests exist.

---

## Do Not Silence Type Errors Casually

A type error should normally be fixed, not hidden.

Before ignoring a warning, ask:

```text
Is the code actually unclear?
Can a better type fix this?
Can the function be simplified?
Is this caused by a dynamic framework or untyped library?
```

If an ignore is truly necessary, it should be narrow and explained.

Example:

```python
# pyright: ignore[reportUnusedFunction] ; REASON: used indirectly by decorator
```

ADR 24 explains the rule for type-checker ignores: suppressions should be controlled, line-specific, and documented with a reason. Read it when the type checker reports something that appears to be a false positive.

---

## Quality Gates: Where This Fits

Linting and type checking are also part of the project’s quality gates.

ADR 22 explains the broader branching, promotion, and release process. For day-to-day coding, the important part is that feature-to-dev promotion expects configured linter checks to pass and the type checker to report no errors.

Read ADR 22 when preparing code for promotion or when checking which quality gates apply before moving changes from one maturity level to the next.

This section is only the practical coding-level overview. ADR 22 contains the process-level rules.

---

## Debugging Setup

`launch.json` contains the VS Code debug configurations for frontend debugging, backend debugpy attach, and Locust debugpy attach. Use it when you need interactive debugging instead of print-based debugging.

This is separate from linting and typing, but it belongs to the same developer feedback loop:

```text
linting catches style and simple correctness issues
typing catches structural mismatches
tests catch behavior problems
debugging helps investigate runtime behavior
```

---

## Practical Development Loop

A good local workflow is:

```text
write code
save file so formatting runs
read editor type/lint feedback
fix warnings while the context is still fresh
run make ruff
run the relevant tests
review the diff
```

This keeps problems small and close to the line where they were introduced.

---

## Checklist Before Committing

Before committing backend code:

```text
Save changed Python files.
Run make ruff.
Check Pyright/Pylance problems in VS Code.
Fix typing issues instead of hiding them.
Use precise, meaningful types.
Run the relevant tests.
Review the diff after auto-formatting or auto-fixes.
```

Short version:

```text
Format early.
Lint early.
Type-check early.
Test after the code is structurally clean.
```
