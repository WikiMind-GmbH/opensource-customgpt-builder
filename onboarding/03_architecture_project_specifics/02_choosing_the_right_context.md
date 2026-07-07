## Leitfaden: Does a Feature Need a New Context?

When adding a feature or use case, do not start by asking:

```text id="9z3gq2"
Where is it easiest to put the code?
```

Start by asking:

```text id="qhz4m3"
Which business capability owns this responsibility?
```

A bounded context is not just a folder. It is an ownership boundary for language, rules, and model decisions.

---

## Step 1: Describe the Feature in Business Language

Write down the feature without technical implementation details.

Good:

```text id="ywkxce"
Users can upload documents so the assistant can answer questions based on them.
```

Less useful:

```text id="6ot9m3"
Add an endpoint that stores PDFs and creates embeddings.
```

The first version describes a business capability.
The second version already jumps into technical implementation.

DDD starts with the business responsibility.

---

## Step 2: Identify the Main Concept

Ask:

```text id="mts18g"
What is the main domain concept this feature changes or introduces?
```

Examples:

```text id="8moy0e"
Conversation
Message
Assistant configuration
Instruction
Document
Knowledge source
Retrieved evidence
```

Then map the concept to the owning context:

```text id="h239t9"
Conversation / Message / prompt composition -> Chat
Assistant configuration / instructions       -> CustomGPT
Documents / retrieval / evidence             -> Knowledge
```

A feature usually belongs where its main concept belongs.

---

## Step 3: Identify the Reason for Change

Ask:

```text id="8p8omo"
If this feature changes later, why will it change?
```

This is one of the most useful questions.

Examples:

```text id="0v6ut8"
It changes because the conversation flow changes.
  -> likely Chat

It changes because assistant configuration rules change.
  -> likely CustomGPT

It changes because document processing or retrieval changes.
  -> likely Knowledge
```

A context should group things that change for the same business reasons.

If two parts change for very different reasons, they probably should not be forced into the same model.

---

## Step 4: Identify the Language Used by the Feature

Ask:

```text id="yv72sh"
Which context's language is needed to describe this feature naturally?
```

Examples:

```text id="zy05zq"
"message", "conversation", "system prompt", "assistant response"
  -> Chat language

"custom assistant", "instructions", "description", "configuration"
  -> CustomGPT language

"document", "chunk", "source", "retrieved evidence", "knowledge"
  -> Knowledge language
```

If a feature mostly uses one context’s language, that is a strong signal that it belongs there.

If it mixes language from several contexts, separate the orchestration from the owned responsibilities.

---

## Step 5: Decide Whether It Is Ownership or Collaboration

Many features require collaboration between contexts.

That does not mean the whole feature belongs in one giant context.

Example:

```text id="ifbl0g"
User asks a question.
Chat needs conversation history.
Chat needs CustomGPT instructions.
Chat needs relevant knowledge.
Chat calls the LLM.
```

This use case involves all three contexts, but ownership is still clear:

```text id="rsjxxq"
Chat owns the conversation and final LLM request composition.
CustomGPT owns assistant configuration.
Knowledge owns retrieval and evidence.
```

The use case may be orchestrated in Chat because the final user-facing action is conversation continuation. But Chat should consume CustomGPT and Knowledge through explicit boundaries, not by importing their internal models.

---

## Step 6: Check Whether Existing Contexts Fit

Before creating a new context, ask:

```text id="s81wxe"
Does this feature clearly belong to Chat?
Does it clearly belong to CustomGPT?
Does it clearly belong to Knowledge?
```

Use this simple decision table:

```text id="uwo25g"
Question                                                     Likely context

Is it about conversation history, messages, or replies?       Chat
Is it about final prompt / LLM request composition?           Chat
Is it about assistant identity, instructions, or settings?    CustomGPT
Is it about documents, chunks, retrieval, or evidence?        Knowledge
Is it only needed to support another context technically?     Infrastructure/adapter, not a new context
Is it a cross-context user flow?                              Usually orchestrated by the context owning the user action
```

A new feature should go into an existing context when it extends that context’s existing business responsibility.

---

## Step 7: When to Consider a New Context

A new bounded context may be justified when the feature introduces a business capability with its own language, rules, and lifecycle.

Signals for a new context:

```text id="oi671q"
The feature introduces concepts that do not naturally belong to Chat, CustomGPT, or Knowledge.
The feature has its own business rules and invariants.
The feature would make an existing context conceptually messy.
The feature changes for different reasons than the existing contexts.
The feature would be useful independently from the current contexts.
The feature needs its own DTO contracts and ownership boundary.
```

Example:

```text id="9o3e6i"
User billing, subscriptions, and payment status
```

This should probably not be forced into Chat, CustomGPT, or Knowledge.

It has its own concepts:

```text id="vdipdu"
subscription
invoice
payment
plan
billing period
```

It also changes for different reasons: pricing, accounting, payment provider integration, access rights, and billing rules.

That is a strong candidate for a separate context.

---

## Step 8: When Not to Create a New Context

Do not create a new context only because:

```text id="v21rij"
the feature needs a new table
the feature needs a new endpoint
the feature needs a new adapter
the code feels large
there is a new external API involved
there is a new background task
```

These are technical reasons, not necessarily domain reasons.

A new table may still belong to an existing context.
A new endpoint may still call an existing use case.
A new external API may just be an adapter behind an existing port.

A bounded context should be created for a business boundary, not for every technical component.

---

## Step 9: Watch for Context Leakage

A feature is probably in the wrong place if it forces one context to speak another context’s language.

Examples:

```text id="u8vfdo"
Knowledge starts returning system prompts.
CustomGPT starts returning message lists.
Chat starts managing document chunking rules.
Knowledge starts owning assistant configuration.
CustomGPT starts deciding conversation ordering.
```

These are warning signs.

A context should return its own domain outputs.

Good:

```text id="93061f"
Knowledge returns retrieved evidence.
CustomGPT returns assistant configuration.
Chat maps both into the final LLM request.
```

Bad:

```text id="yf1y7m"
Knowledge returns Chat messages.
CustomGPT returns system prompts.
```

This rule follows the same reasoning as ADR 27: prompt and conversation composition belong to Chat, while provider contexts return domain outputs rather than conversation-shaped artifacts.

---

## Step 10: Decide the Use Case Owner

Some use cases involve multiple contexts. In that case, choose the owner by asking:

```text id="a1y2hq"
Which context owns the user-visible outcome?
Which context owns the state transition?
Which context owns the main invariant?
Which context would be wrong if this use case behaved incorrectly?
```

Examples:

```text id="tsk8to"
"Send a message and receive an assistant response"
  -> Chat owns the use case.
  It may call CustomGPT and Knowledge.

"Update assistant instructions"
  -> CustomGPT owns the use case.
  Chat may later consume the updated configuration.

"Upload a document for retrieval"
  -> Knowledge owns the use case.
  Chat may later consume retrieved evidence.

"Use retrieved evidence in an answer"
  -> Chat owns prompt composition.
  Knowledge owns retrieval.
```

This distinction is important:

```text id="lwo68b"
Owning a use case does not mean owning all data used by the use case.
```

---

## Step 11: Define the Boundary Contract

When a feature crosses contexts, define an explicit boundary.

Ask:

```text id="ceve8s"
What does the consuming context need?
What should the providing context expose?
Which DTO represents the contract?
Where does mapping happen?
Which errors belong to the contract?
```

The contract should not expose internal models.

Avoid:

```text id="zbv2i0"
Chat imports KnowledgeDocumentEntity.
Knowledge returns ChatMessageDTO.
CustomGPT exposes ORM models.
```

Prefer:

```text id="w4ydff"
Knowledge returns RetrievedEvidenceDTO.
CustomGPT returns CustomGptConfigurationDTO.
Chat maps those DTOs into Chat-owned prompt structures.
```

---

## Step 12: Make the Decision Explicit

For small features, the decision may only need to be visible in the code structure and naming.

For larger features, or when ownership is debatable, document the reasoning.

A short decision note is enough:

```text id="mtdd36"
Feature: Use retrieved document evidence in assistant responses

Decision:
- Knowledge owns document retrieval and evidence.
- Chat owns final prompt composition.
- Knowledge returns RetrievedEvidenceDTO.
- Chat maps evidence into Chat-owned prompt structures.
- Knowledge must not return system prompts or message-shaped objects.

Reason:
This keeps retrieval language separate from conversation language and follows the Chat ownership rule for prompt composition.
```

If the decision changes architecture, boundaries, dependency direction, or DTO ownership, create or update an ADR.

---

## Summary

Use this short decision flow:

```text id="4s3vmj"
1. Describe the feature in business language.
2. Identify the main domain concept.
3. Ask why the feature will change in the future.
4. Match the language to an existing context.
5. Separate ownership from collaboration.
6. Use existing contexts when the responsibility fits.
7. Create a new context only for a real new business capability.
8. Watch for context leakage.
9. Define explicit DTO contracts across boundaries.
10. Document debatable decisions.
```

The most important rule:

```text id="2ovpk2"
Put behavior where the business responsibility belongs,
not where the implementation is easiest.
```
