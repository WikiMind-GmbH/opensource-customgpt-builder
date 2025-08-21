## Runtime View
### Upload documents and RAG functionality
Uploading and processing a document is notably done in two steps and utilizes two different message protocols.  

For the client to be able to get live-updates about uploaded documents having been processed and being available to use in the chat, the client must subscribe to the Websocket Endpoint first.
![](embed:wsMessage)

The client uploads a document and gets a response message as soon as the file has been saved to the files system. The background task is queued before sending the response
![](embed:uploadDocument)

After the response of the RagServiceAPI has been sent, the background task starts with the (pre)processing. After this is finished, the client gets a WebsocketMessage informing them that their document is available to the chatbot.
![](embed:processDocument)