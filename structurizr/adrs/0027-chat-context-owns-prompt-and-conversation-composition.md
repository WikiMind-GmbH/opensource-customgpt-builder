# 27. Chat context owns prompt and conversation composition

Date: 2026-03-10

A short, descriptive statement of the architectural decision.
It should be specific enough to be understandable without reading the full document.

## Status

Accepted

Supercedes [0004](0004-RAG,-CustomGPT-serve-raw-data-to-Chatservice.md)

Supercedes [Who owns sysprompt generation](0012-prompt-engineering-ownership.md)

## Created by

List all contributors who have meaningfully edited this ADR.
Version history in Git provides the authoritative change log.

## Decision Maker

The person responsible for approving this ADR and moving it from OPEN/PROPOSED to ACCEPTED.

This should be the person accountable for software architecture decisions.
Only this person may mark the ADR as ACCEPTED.



## Scope

## Scope

Applies to:
- Chat, RAG, and CustomGPT bounded contexts (and any future context that contributes information to an LLM call)
- all prompt-related artifacts: system prompts, message lists, role assignment, formatting/templating, truncation/token budgeting, merging context inputs
- tool-calling configuration as part of the final LLM request (selection and shaping of tool specs for a call)

Does **not** prescribe:
- concrete DTO schemas of RAG/CustomGPT outputs (see boundary DTO ADRs)
- implementation details of caching, pub/sub, or runtime optimization
- detailed tool-calling architecture beyond ownership and boundary rules

## Context

We want clear responsibilities and minimal coupling between bounded contexts in our modulith.

The Chat context is responsible for producing the final input to the LLM call. That input is composed from:
- user message + prior conversation history (Chat domain)
- retrieved evidence (RAG domain)
- CustomGPT configuration/instructions (CustomGPT domain)
- possibly tool availability/specification and other metadata

Two problematic alternatives regularly appear:
1) Provider contexts (RAG, CustomGPT) return conversation-shaped artifacts (e.g., system prompts, message lists, `{role, content}`-like structures).
2) Prompt responsibilities are split across contexts, leading to unclear ownership, duplicated logic, and brittle changes.

If provider contexts return conversation-like artifacts, we couple them to Chat’s domain language and prompt conventions. This undermines bounded-context separation, makes changes harder (e.g., tool calling, message formatting rules), and creates contradictions about “who owns prompt generation”.

Additionally, prompt composition must remain up-to-date when underlying provider data changes (e.g., CustomGPT properties). Centralizing composition in Chat makes update strategies (fresh fetch, caching, invalidation) a Chat-owned orchestration concern rather than leaking cross-context coupling into provider contracts.

## Alternatives Considered

1) **Providers return conversation-like artifacts (system prompt / message list)**
- Advantages:
  - Less composition work in Chat initially
  - Providers can encapsulate formatting decisions
- Disadvantages:
  - Leaks Chat concepts (messages/roles/system prompts) into other contexts
  - Splits prompt conventions across contexts, reduces cohesion
  - Forces providers to change when Chat prompt structure changes (e.g., tool calling format)
  - Encourages “renamed Chat DTOs” and coupling
- Not chosen because it violates bounded-context separation and creates long-term maintenance costs.

2) **Each provider returns “its own prompt fragment” and Chat concatenates**
- Advantages:
  - Providers retain more control over how their data is presented
- Disadvantages:
  - Still splits prompt engineering across contexts
  - Fragment boundaries become ambiguous and evolve unpredictably
  - Harder to enforce consistency, safety guardrails, and token budgeting
- Not chosen because it still distributes prompt responsibility.

3) **Chat context owns prompt composition; providers return domain outputs (chosen)**
- Advantages:
  - Single clear owner of prompt engineering and final LLM request shape
  - Providers remain cohesive and focused on their domain responsibilities
  - Reduces coupling; Chat can degrade gracefully if a provider is unavailable
  - Tool calling and future LLM request changes are localized to Chat
- Disadvantages:
  - Chat contains more orchestration/mapping logic
  - Requires disciplined boundary DTO design and mapping

## Decision

1) **Chat context is the single owner of prompt/conversation composition**
Only the Chat context may produce or manage conversation/prompt artifacts such as:
- system prompt generation
- message assembly (including roles and ordering)
- formatting/templating and merging multiple inputs into the final LLM request
- truncation/token budgeting decisions
- shaping the final “tools” payload for a call (if tools are enabled)

2) **Provider contexts return domain outputs, not conversation-shaped artifacts**
RAG and CustomGPT (and similar contexts) must return only their domain outputs via DTOs (evidence/configuration), and must never return:
- system prompts
- message lists
- conversation snippets
- role/content-shaped structures that mirror Chat concepts

3) **Chat maps provider outputs into Chat prompt constructs**
Chat consumes provider DTOs and performs the mapping into Chat-owned prompt structures.
Mapping logic lives in the Chat context (or its internal orchestration/mapping modules), not in provider contexts and not inside provider contracts.

4) **Freshness is a Chat orchestration concern**
Ensuring that prompt composition reflects current provider data (e.g., updated CustomGPT properties) is handled by Chat’s orchestration strategy (fresh fetch, caching, invalidation), without pushing “precomposed prompt” responsibilities into provider contexts.

## Consequences

Benefits:
- Clear responsibility: prompt engineering is centralized and consistent.
- Stronger bounded-context separation: providers do not model Chat concepts.
- Easier evolution: changes to prompt format, safety guardrails, or tool calling are localized to Chat.
- Improved resilience: Chat can continue (with reduced context) if RAG/CustomGPT are temporarily unavailable.

Trade-offs / costs:
- Chat becomes the integration point and must implement mapping and assembly.
- Requires discipline to prevent “prompt fragment creep” back into provider contexts.
- Some duplication risk: providers may still want to present data a certain way; that preference must be expressed as domain metadata, not prompt text.

Risks and mitigations:
- Risk: providers start returning “almost messages” (renamed leakage).
  - Mitigation: code reviews enforce the “no conversation-shaped artifacts” rule; boundary DTO ADR provides guidance.
- Risk: Chat prompt logic becomes complex.
  - Mitigation: treat prompt composition as a first-class module with tests and clear sub-components (evidence formatting, CustomGPT instruction integration, tool shaping).

Follow-up work:
- Supercede the previous ADRs that split/contradicted ownership (ADR 0004 and ADR 0012).
- Refactor existing CustomGPT↔Chat and RAG↔Chat ports/adapters to return only domain outputs (DTOs), not system prompts or message-like structures.