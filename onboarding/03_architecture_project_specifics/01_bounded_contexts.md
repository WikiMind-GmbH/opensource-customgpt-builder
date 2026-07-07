## Why We Separate Chat, CustomGPT, and Knowledge

In our current architecture, each subdomain is implemented as exactly one bounded context. This is a deliberate first-iteration rule: one business capability maps to one code boundary. The system is still deployed as one modulith, but internally it is structured as independently evolvable bounded contexts with clear contracts.

For our domain, we currently separate three central subdomains:

```text id="klp9x4"
Chat
CustomGPT
Knowledge
```

Each of them owns a different part of the business problem.

Check the C4-Diagrams illustrating our projects_architecture

---

### Chat

The **Chat** context owns the conversation experience.

It is responsible for things like:

```text id="n6oh3p"
conversation history
user messages
assistant messages
message ordering
final prompt composition
final LLM request shape
```

Chat is the place where the final input to the LLM is assembled.

This does not mean Chat owns all information used in the prompt. It means Chat owns the decision of how different inputs are combined into a conversation or prompt structure.

---

### CustomGPT

The **CustomGPT** context owns the configuration of a custom assistant.

It is responsible for things like:

```text id="0yrmsw"
assistant name
description
instructions
configuration
available behavior-defining metadata
```

CustomGPT should not decide how a conversation is assembled.

It provides domain information about the configured assistant. Chat then decides how that information is used in the final prompt.

---

### Knowledge

The **Knowledge** context owns knowledge retrieval and knowledge-related data.

Depending on the concrete feature, this can include things like:

```text id="erplor"
documents
document chunks
retrieved evidence
source metadata
relevance information
embedding-related data
```

Knowledge should not decide how a chat conversation is structured.

It provides domain information that may be useful for answering a user message. Chat then decides how retrieved evidence is included in the final LLM request.

---

## Why These Are Separate Contexts

We separate these contexts because they have different responsibilities and different reasons to change.

```text id="34xor0"
Chat changes when conversation behavior or prompt composition changes.
CustomGPT changes when assistant configuration behavior changes.
Knowledge changes when document handling or retrieval behavior changes.
```

If we mixed these into one model, the boundaries would become unclear.

For example, a “message” belongs to Chat.
A “CustomGPT instruction” belongs to CustomGPT.
A “retrieved evidence snippet” belongs to Knowledge.

All three may contribute to one LLM call, but that does not mean they are the same concept or should live in the same context.

The boundary helps us keep each model focused.

---

## Example: ADR 27 and Deciding Where Something Belongs

ADR 27 is a good example of how we decide context ownership.

The question was:

```text id="e1ac92"
Who owns prompt and conversation composition?
```

Several options were possible:

```text id="kwieox"
CustomGPT could return a system prompt.
Knowledge could return prompt fragments.
Each provider could return message-like structures.
Chat could assemble everything itself.
```

The chosen decision is that **Chat owns prompt and conversation composition**. Only Chat may produce or manage prompt/conversation artifacts such as system prompts, message assembly, role ordering, formatting, truncation, token budgeting, and final tool payload shaping.

Provider contexts such as CustomGPT and Knowledge must return domain outputs, not conversation-shaped artifacts. ADR 27 explicitly says that providers must not return system prompts, message lists, conversation snippets, or role/content-shaped structures that mirror Chat concepts.

That means:

```text id="z9bqwc"
CustomGPT returns assistant configuration.
Knowledge returns retrieved evidence.
Chat maps both into Chat-owned prompt structures.
```

This is important because if CustomGPT or Knowledge returned message-like objects, they would start depending on Chat’s language. That would weaken the bounded context separation and make later changes harder. ADR 27 calls out exactly this risk: provider contexts returning conversation-like artifacts would couple them to Chat’s prompt conventions and split prompt responsibility across contexts.

---

## Boundary Rule

The practical rule is:

```text id="9yxzb4"
A context owns its domain concepts.
A context does not return another context’s internal concepts.
Data crossing context boundaries uses explicit DTOs.
The receiving context maps those DTOs into its own model.
```

This follows the general boundary DTO rule: data crossing a boundary must use contract-owned DTOs, not internal domain entities, ORM models, SDK objects, or renamed copies of another side’s internal model.

So when deciding where something belongs, ask:

```text id="tg8kes"
Is this about conversation structure? -> Chat
Is this about assistant configuration? -> CustomGPT
Is this about documents, retrieval, or evidence? -> Knowledge
Is this about composing the final LLM request? -> Chat
```

The goal is not to prevent collaboration between contexts.

The goal is to make collaboration explicit, with clear ownership and stable contracts.


