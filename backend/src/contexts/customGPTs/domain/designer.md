## Use cases

### A user sends a message in a conversation
We get the user text. 
1) Then we retreive a conversation if it is there. 
If it is not there, we create a new conversation object. 
2) Then we must check if a customgpt is selected. If yes: add the customgpt context to the conversation. 
3) Then we add the user message to the conversation. 
5) Send conversation to openaiApi adapter
Expose tool call: retreive_relevant_chunks_of(Conversation) -> add context to conversation
6) Add assistant message (which might contain tool call) to conversatioin
7) commit conversation and return answer to user

### A user retreives 
