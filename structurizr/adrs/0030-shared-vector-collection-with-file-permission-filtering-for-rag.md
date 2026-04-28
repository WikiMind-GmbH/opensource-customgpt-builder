# 30. Shared Vector Collection with File-Permission Filtering for RAG

Date: 2026-04-28

RAG stores file embeddings once in a shared vector collection and filters retrieval by the file permissions of the current CustomGPT.

## Status

PROPOSED -chatgpt prompt to create adr for this decision

## Created by

Albert Sandritter

## Decision Maker

Albert Sandritter

## Scope

Applies to RAG retrieval for CustomGPT-accessible uploaded files.

Applies to:
* file chunk embeddings
* vector-store collection structure
* CustomGPT-to-file permission handling during retrieval

Does not decide:
* concrete chunking strategy
* embedding model choice
* concrete Qdrant index configuration beyond requiring an indexable `file_id` payload field

## Context

Files can be attached to CustomGPTs. The same file may be usable by multiple CustomGPTs.

Creating chunks and embeddings repeatedly per CustomGPT would waste compute and storage. At the same time, RAG retrieval must only return chunks from files the current CustomGPT may access.

Permissions can change over time, so the system needs a clear source of truth and a retrieval strategy that avoids stale authorization data.

## Alternatives Considered

### 1. Shared vector collection filtered by accessible file IDs

Store each file’s chunks and embeddings once. Store permissions in the relational database. At retrieval time, load accessible file IDs for the CustomGPT and query the vector store with a `file_id` filter.

Pros:
* embeddings are not duplicated
* permission source of truth stays in the relational database
* permission changes do not require updating existing vectors
* simple consistency model

Cons:
* RAG retrieval needs one permission lookup before vector search
* vector search uses a potentially long filter

Chosen.

### 2. Store CustomGPT IDs in vector payload

Store permitted CustomGPT IDs directly on each vector and filter by CustomGPT ID.

Pros:
* vector query filter is simple
* no pre-query file ID lookup needed

Cons:
* duplicates permission state in the vector store
* permission changes require updating all affected chunk vectors
* stale payload data could cause incorrect retrieval authorization

Not chosen initially.

### 3. One vector collection per CustomGPT

Create a separate vector collection for each CustomGPT.

Pros:
* retrieval logic is simple
* no permission filter needed

Cons:
* duplicates chunks and embeddings for shared files
* increases storage and embedding cost
* file updates/deletes become more complex
* many collections increase operational overhead

Not chosen.

## Decision

Use one shared vector collection per embedding model/vector dimension.

Each file is chunked and embedded once. Each vector point stores at least:

* `file_id`
* chunk metadata needed for retrieval

The relational database permission table remains the source of truth for which CustomGPT may access which file.

RAG retrieval works as follows:

1. Resolve all file IDs accessible to the current CustomGPT from the relational database.
2. Query the vector store with a filter restricting results to those `file_id`s.
3. Return only matching chunks.

The vector-store adapter must support filtered search by `file_id`.

The `file_id` payload field must be suitable for indexing in the vector store.

## Consequences

Benefits:
* avoids duplicate embeddings for files shared by multiple CustomGPTs
* keeps permission truth in one place
* permission changes do not require vector payload updates
* keeps vector store as a retrieval index, not an authorization source of truth

Trade-offs:
* each RAG retrieval requires a permission lookup
* vector queries include a potentially long `file_id` filter
* performance must be validated with realistic file and chunk counts

Risks:
* very large permission sets may make filtered vector search slower
* missing or incorrect vector-store payload indexing may hurt retrieval performance

Mitigations:
* index the `file_id` payload field
* add performance tests with realistic numbers of files, chunks, and accessible file IDs
* only consider denormalizing CustomGPT permissions into vector payload if benchmarks show the chosen design is insufficient