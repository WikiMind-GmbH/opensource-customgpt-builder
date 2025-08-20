workspace "CustomGPT" "Use Chatgpt api with own customGPT implementation"{
    // this enables us to write ss.containername instead of just containername -
    !identifiers hierarchical 


    model {
        u = person "User" "A user of the system wanting to profit from customized llm chat functionality" "Person"
        ss = softwareSystem "Opensource CustomGPT builder"{
            react = container "Frontend" "A web app for chat with custom gpts and your data" "React + TS" "Web Browser"
            gateway = container "Gateway" "This gateway routes requests to the correct microservice" "Fastapi"
            chatservice = container "ChatService" "Provides llm chat functionality and composes llm prompts from raw data -userinput, customgpt, rag"{
                api = component "ChatserviceApi" "API for chatting with LLMs utilizing Additional data from other services"
                db = component "ConversationDB" "Stores the conversation histories and metadata of the conversation"{
                    tags "Database"
                    technology "SQLite"
                }
            }
            customgptService = container "CustomGPTService" "Stores and Serves basic CustomGPT information"{
                api = component "CustomGptApi""API to set and query the Basic information as well as composing conversation snippets to be utilized in new chats which use this"
                db = component "CustomGptDB" "Stores the basic information of the CustomGPTs"{
                    tags "Database"
                    technology "SQLite"
                }
            }
            ragService = container "RagService" "Retreive fitting document chunks and provide an api to add or update data"{
                api = component "RagServiceAPI" "API for processing&storing raw data in a vector database and retreiving relevant chunks and raw data"
                vectorDB = component "vectorDB"{
                    tags "Database"
                    technology "Qdrant"
                }
                metadataDB = component "MetadataDB"{
                    tags "Database"
                    technology "SQLite"
                }
                backgroundTask = component "Background Task" "Queue tasks to continue directly after responding"
                localFS = component "Local File System" "Used to store non-processed and pre-processes  whole documents"
                githubDataService = component "githubDataService" "Listens for notification updates from github and updates the corresponding data in the vectorDB"
            }

            !docs docs
            !adrs adrs
            
        }
        openaiapi = softwareSystem "OpenAIApi" "Pass conversation and Retreive assistant messages of OpenAI LLMs" "External System" 
        github = softwareSystem "github" "Sends a Post message to all subscribers whenever a new commit was made" "External System" {
            webhook = container "githubWebhook" "Listens for new commits and sends Post call to specific url"
            api = container "GithubAPI" "Provides api for interacting with github repos, e.g. retreiving data"
        }

        u -> ss.react "Chats with LLM, uploads data and creates or uses CustomGPTs using" "RestAPI"
        ss.react -> ss.gateway "Gets conversations, assistantersponses and data from and send user messages and data to"
        ss.gateway -> ss.chatservice.api "Gets or creates conversations with LLMs, optionally utilizing RAG and CustomGPT data, utilizing the" "RESTApi"
        ss.chatservice.api -> ss.chatservice.db "Stores and retreives Conversations -including metadata- to and from" "SQLModel"
        ss.chatservice.api -> ss.customgptService.api "Retreive infromation about CustomGPTs from" "RESTApi"
        ss.chatservice.api -> ss.ragService.api "Sends text-snipet and gets relevant document chunks and their metadata from"
        ss.chatservice.api -> openaiapi "Sends conversation (snippets) to get assistant messages as answers from" "RESTApi"
        
        
        ss.gateway -> ss.customgptService.api "Gets or creates CustomGPTs utilizing"
        ss.customgptService.api -> ss.customgptService.db "Stores and retreives CustomGPT information -including metadata- to and from" "SQLModel"

        ss.gateway -> ss.ragService.api "Sends documents to process and embedd and retreives relevant document chunks to a given text from"
        ss.ragService.api -> ss.ragService.localFS "store unprocessed and processed whole documents on"
        ss.ragService.api -> ss.ragService.backgroundTask "query processing tasks"
        ss.ragService.api -> openaiapi "create embeddings for chunks of documents utilizing"
        ss.ragService.api -> ss.ragService.vectorDB "store and retreive (similar) document chunks embeddings"
        ss.ragService.api -> ss.ragService.metadataDB "store metadata information about documents stored in the VectorDB"

        ss.ragService.api -> ss.gateway "Sends messages when the processing status of uploaded documents has changed" "RESTApi"
        ss.gateway -> ss.react "Sends messages when the processing status of uploaded documents has changed to" "WSMessage"
        
        github.webhook -> ss.ragService.githubDataService "Notifies about new commits" "POST Call"
        ss.ragService.githubDataService -> github.api "retreives repository content from"
        ss.ragService.githubDataService -> ss.ragService.api "updates outdate github repo data in"
        
        



        
    }

    views {
        systemContext ss "SystemContex"{
            include *
            // autoLayout lr
        }
        container ss "ContainerView"{
            include *
            // autoLayout lr
        }
        component ss.chatservice "chatserviceView"{
            include *
            exclude "element.type==Container -> element.type==Container"
            exclude "element.type==SoftwareSystem -> element.type==Container"
            exclude "element.type==Container -> element.type==SoftwareSystem"
            // autoLayout lr
        }

        component ss.ragService "ragServiceView"{
            include *
            exclude "element.type==Container -> element.type==Container"
            exclude "element.type==SoftwareSystem -> element.type==Container"
            exclude "element.type==Container -> element.type==SoftwareSystem"
            // autoLayout lr
        }

        component ss.customGPTService "customGPTServiceView"{
            include *
            exclude "element.type==Container -> element.type==Container"
            exclude "element.type==SoftwareSystem -> element.type==Container"
            exclude "element.type==Container -> element.type==SoftwareSystem"
            // autoLayout lr
        }

        dynamic ss.ragService {
            title "upload document and start processing" 
            u -> ss.react "Uploads document to"
            ss.react -> ss.gateway "sends document file via Post call to"
            ss.gateway -> ss.ragService.api "send document to"
            ss.ragService.api -> ss.ragService.localFS "store original document in"
            ss.ragService.api -> ss.ragService.metadataDB "adds document infomation to and set status to uploaded"
            ss.ragService.api -> ss.ragService.backgroundTask "query processing background task"
            ss.ragService.api -> ss.gateway "notifies about the successful upload of the document"
            ss.gateway -> ss.react "notifies about the successful upload of the document"
        }

        dynamic ss.ragService {
            title "uploaded document finished processing"
            ss.ragService.backgroundTask -> ss.ragService.api "trigger preprocessing of the document"
            ss.ragService.api -> ss.ragService.localFS "save preprocessed (whole) document"
            {
                ss.ragService.api -> ss.ragService.metadataDB "update metadata information to note preprocessed document"
            }
            {
                ss.ragService.api -> openaiapi "create embeddings for created document chunks utilizing"
            }
            ss.ragService.api -> ss.ragService.vectorDB "store embeddings in"
            ss.ragService.api -> ss.ragService.metadataDB "sets document status to available and updates other metadata information"
            ss.ragService.api -> ss.gateway "notifies about the successful proccesing of the document"
            ss.gateway -> ss.react "send notification about availability of the document to subscribed" "WSMessage"
        }

        dynamic ss {
            title "client subscibes to websocketMsg"
            ss.react -> ss.gateway "subscribes to websocketmessages"
        }

        dynamic ss.customgptService {
            title "create or edit custom gpt"
            ss.react -> ss.gateway "send customgpt form data to"
            ss.gateway -> ss.customGPTService.api "forwad post call to"
            ss.customGPTService.api -> ss.customGPTService.db "save data and metadata in"
            ss.customGPTService.api ->  ss.gateway "success response"
            ss.gateway -> ss.react "success response"
        }


        styles {
            element "Person" {
                color #ffffff
                fontSize 22
                shape Person
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "External System" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Web Browser" {
                shape WebBrowser
            }
            element "Database" {
                shape Cylinder
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "Failover" {
                opacity 25
            }
        }
    }
}