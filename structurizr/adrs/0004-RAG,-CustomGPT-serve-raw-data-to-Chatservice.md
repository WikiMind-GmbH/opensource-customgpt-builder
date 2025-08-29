# RAG, CustomGPT serve raw data to Chatservice instead of conversationsnippets

Date: 2025-08-04

## Status

ACCEPTED    

## Context

When composing a text, we will not only take into account the user input but also relevant data of the rag system as well as the data stored in the customgpt service.   
Now theoretically, the RAG Service or customgpt service could process their raw data before giving it back to the chatservice.   
I.e. the customgpt service could return not just the values of the description, name, id of the customgpt. It could already process this data and transform it into a conversation object for the chatservice -i.e. a system prompt.   
Same for the Rag Service.

Responsibility, cohesion and coupling are swa concepts which measure how well a system can be maintained and read.  
We now have to decide where these functionalities make the most sense.   


## Decision
If the chat service composes conversations of the user message, previouse history and so on, it would be fitting that it also composes the messages from the other raw data as well.   
In this way, the chatservice is soley for composition of the conversation out of raw data and the customgptservice as well as the RAG Service are soley responsible for providing the raw data.   
In this way, the responsibility of prompt engineering is not split across services and the sole resposnibility of the chatservice.   
This also makes the services more cohesive: The RAG and customgpt service are only responsible for data management and not prompt engineering. Also the domain model of conversations should be found in the chatservice, it is no concept related to RAG nor CustomGPT.  

(We will also lessen the coupling between these services by enabling the chatservice to still respond, even if the other services are not reachable. However, then the user will be notified)




## Consequences

The interfaces/apis of the customgpt as well as the RAG service will provide the 'raw' data in a well readable format. They will not return conversation-snippets or do any kind of prompt-engineering.   
Any Prompt-engineering is the responsibility of the chatservice.