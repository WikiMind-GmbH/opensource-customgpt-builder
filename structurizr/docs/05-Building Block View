## Buildig Block view -C4 System Context View
![](embed:SystemContex)

### Whitebox overall system- C4 Container Views
![](embed:ContainerView)

### Level 2 - C4 Component Views
#### ChatService
![](embed:chatServiceView)
The chat service has the following apis:
```
createConversation(CustomGptId:int | None, usermessage: str, useRag:bool)
continueConversation(conversationid::int | None , usermessage: str, useRag:bool)
```
If a CustomGPTid is given, the CustomGPTservice api is called to retreive Infos about the customgpt. If the customGPTservice is not reachable, the request will be processed without the customGPT, but the answer will include this information.
Same for the RAG Service. This is due to decoupling and keeping the service running even if the other services are down.

The Rag service will return relevant chunks, but will not process them. How we tune&enrich our prompt with the retreived chunks is decided by the chatservice, not in the rag service, to keep responsibilities clear.

#### RAGService  
![](embed:ragServiceView)
The Rag service offers the following functionality: 
- upload documents that can be referenced by the llm if relevant
- send a notification if uploaded documents have been processed and can be  
The Rag service provides an api for retreiving the status of uploaded documents: it is either uploaded or available(processed)

The RagService will use WebsocketMessages (/async messages)to inform other services when uploaded documents have been processed. (The initial sync Data uoload api will retrurn a success msg as soon as the files have been uploaded and will then use the WSMessage to nitify when everything has been processed)

For simplicity, documents will be identified by the following: `customgpt_id: int | None, document_name` if `customgpt_id` is None, the document is available for all chats, not just a specific customgpt.



#### CustomGPTService
![](embed:customGptServiceView)
Database schema sketch: 
`id:int, name:str, description:str, rag_files_availability: json_str`
Where `rag_files_availability` is a dictionary where the keys are the names of the documents and the values are either `uploaded` or `processed`

Decouopling&eventual consistency: The customGPTService will have a 