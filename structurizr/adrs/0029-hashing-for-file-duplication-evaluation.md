# 29. hashing for file duplication evaluation

Date: 2026-04-15

We must design a process on how we can use hashing best to achieve a system that correctly determines if a file with the same pure document content has been uploaded before.


## Status

Open

## Created by

<!-- List all contributors who have meaningfully edited this ADR.
Version history in Git provides the authoritative change log. -->

## Decision Maker

<!-- The person responsible for approving this ADR and moving it from OPEN/PROPOSED to ACCEPTED.

This should be the person accountable for software architecture decisions.
Only this person may mark the ADR as ACCEPTED. -->



## Scope

<!-- Clearly define what this decision applies to (e.g., specific service, repository, bounded context, infrastructure component, or the entire system).

Explicitly state if the decision does **not** apply to certain areas to avoid ambiguity. -->



## Context
There are functional requirements - like avoiding false negatives and false positives and non functional requirements - lower computational cost.

See [here](https://jszym.com/blog/short_input_hash/) for slightly anecdotal research on python hashing function speed 

### Non funcional requirement: Computational cost

We need a hashing algorithm that is not too slow. Because we do not use them for cryptographic reasons, we do not have requirements for security features of hashing algorithms that were designed for cryptography, making our field of canditates wider.

### Avoiding false positives
We must assure that our hash is long enought to avoid false positive duplicates.

### Avoiding false negatives
A lot of file formats also save metadata. E.g. word or pdf. So while the metadata may be different, the actual file contents may be the same. 
Hashing the whole file, instead of 'unzipping' a word document and only hashing the document content can therefore produce false negatives.
There could/should be ways to only hash the 

<!-- Describe:

* The problem or need motivating this decision
* Relevant technical, organizational, or business constraints
* Assumptions made at the time of writing
* Any background information necessary to understand the trade-offs

This section should make it clear *why* a decision is required. -->



## Alternatives Considered

```
Optional format-aware logical deduplication for selected file types where metadata-only differences are common and business-relevant.

For the hashing function itself, prefer:

BLAKE3 if you want best performance and a modern strong hash
SHA-256 if you want maximum standard-library simplicity and zero extra dependency
xxHash only if you explicitly accept a non-cryptographic hash and pair it with a verification step

For most Python backends, the practical choice is:

SHA-256 for simplicity and strong safety
BLAKE3 if performance is important enough to justify one dependency
```



<!-- List the viable alternatives that were evaluated.

For each alternative, briefly describe:

* The approach
* Its advantages
* Its disadvantages
* Why it was not chosen (if applicable)

If the decision was not a simple this-or-that choice, describe the key dimensions and trade-offs that were considered. -->



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
