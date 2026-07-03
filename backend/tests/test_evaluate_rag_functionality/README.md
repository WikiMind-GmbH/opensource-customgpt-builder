## Evaluating RAG performance two ways

There are two goals: 
We want to test the functionality of our retrieval system for ourself and provide the user with a functionality to test and also illustrate the retrieval performance.

There is no one solution for all cases: different data compositions of the document store will necessitate a different solution design. 

However, at the start, we could try to design requirements for a solution that fits most use cases good enough.

## 1) We want to real-life test the rag functionality
That means: 

### test if files are correctly retrieved, even if the file-corpus is large
It is easier to retrieve the 3 correct chunks from a corpus of 300 instead of 300k.
It is easier to retrieve the 3 correct(most relevant) chunks from a corpus of diverse data than from a corpus of very similar data.

Diffent search types (name/keyword vs concepts) favor different retrieval strategies. 
Different documents/modalities favor different retrieval strategies.


---
For that we might want to ingest and keep a large corpus of documents that create the `noise`, making it harder to retrieve the corerct documents. 
The type of documents and the
### Test

## 2) Create tests for the user to evaluate if the retrieval works as expected 
This also leads to the interesting opportunity:
- The tests are not run once at creation time, but rather in intervals, where reruns are triggered if the document store (vector store) has grown a substantial amount.
This would notify the user and us, about performance detioration, signaling that retrieval functionality must be reworked or another error must be fixed..


# Various Solutions&problems
- back-up the database of ingested documents in some shape
- create domain module for evaluator in knowledge context (it might mirror some chat fnx, but whatever; use the llm adapter of chat context and other related if needed)
- Think: what to build first? -> domain?
-