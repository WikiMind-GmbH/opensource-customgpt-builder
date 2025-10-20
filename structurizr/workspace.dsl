workspace "CustomGPT" "Use Chatgpt api with own customGPT implementation"{
    // this enables us to write ss.containername instead of just containername -
    !identifiers hierarchical 


    model {
        u = person "User" "A user of the system wanting to profit from customized llm chat functionality" "Person"
        ss = softwareSystem "Opensource CustomGPT builder"{
            react = container "Frontend" "A web app for chat with custom gpts and your data" "React + TS" "Web Browser"
            interface = container "Interface" "Provides endpoints and calls service functions of the fitting contexts" "Fastapi"
            chatservice = container "ChatService" "Provides chat functionality with an LLM"{
                llmAdapter = component "LLMAdapter" "Processes multiple inputs (sysPrompt, context, messages, tools) to get a response from an LLM completion API"
                core = component "ChatserviceApi" "API for chatting with LLMs utilizing Additional data from other services"
                db = component "ConversationDB" "Stores the conversation histories and metadata of the conversation"{
                    tags "Database"
                    technology "SQLite"
                }
            }
            customgptService = container "CustomGPTService" "Stores and Serves basic CustomGPT information"{
                cgptSyspromptAdapter = component "constructs and returns a sysprompt based on a specific cgpt ID"
                core = component "CustomGptApi""API to get/create/change customgpts"
                db = component "CustomGptDB" "Stores the basic information of the CustomGPTs"{
                    tags "Database"
                    technology "SQLite"
                }
            }
            // ragService = container "RagService" "Retreive fitting document chunks and provide an api to add or update data"{
            //     api = component "RagServiceAPI" "API for processing&storing raw data in a vector database and retreiving relevant chunks and raw data"
            //     vectorDB = component "vectorDB"{
            //         tags "Database"
            //         technology "Qdrant"
            //     }
            //     metadataDB = component "MetadataDB"{
            //         tags "Database"
            //         technology "SQLite"
            //     }
            //     backgroundTask = component "Background Task" "Queue tasks to continue directly after responding"
            //     localFS = component "Local File System" "Used to store non-processed and pre-processes  whole documents"
            //     githubDataService = component "githubDataService" "Listens for notification updates from github and updates the corresponding data in the vectorDB"
            // }

            !docs docs
            !adrs adrs
            
        }
        openaiapi = softwareSystem "OpenAIApi" "Pass conversation and Retreive assistant messages of OpenAI LLMs" "External System"
        // github = softwareSystem "github" "Sends a Post message to all subscribers whenever a new commit was made" "External System" {
        //     webhook = container "githubWebhook" "Listens for new commits and sends Post call to specific url"
        //     api = container "GithubAPI" "Provides api for interacting with github repos, e.g. retreiving data"
        // }

        u -> ss.react "Chats with LLM, creates or uses CustomGPTs using" "RestAPI"
        ss.react -> ss.interface "Gets conversations, assistantersponses and data from and send user messages and data to"
        ss.interface -> ss.chatservice.core "Gets or creates conversations with LLMs, optionally utilizing RAG and CustomGPT data, utilizing the" "RESTApi"
        ss.chatservice.core -> ss.chatservice.db "Stores and retreives Conversations -including metadata- to and from" "SQLModel"
        ss.chatservice.core -> ss.customgptService.cgptSyspromptAdapter "Get the systemPrompt created from the cgpt information from" "RESTApi"
        // ss.chatservice.core -> ss.ragService.core "Sends text-snipet and gets relevant document chunks and their metadata from"
        ss.chatservice.core -> openaiapi "Sends conversation (snippets) to get assistant messages as answers from" "RESTApi"
        
        
        ss.interface -> ss.customgptService.core "Gets or creates CustomGPTs utilizing"
        ss.customgptService.core -> ss.customgptService.db "Stores and retreives CustomGPT information -including metadata- to and from" "SQLModel"

        // ss.interface -> ss.ragService.core "Sends documents to process and embedd and retreives relevant document chunks to a given text from"
        // ss.ragService.core -> ss.ragService.localFS "store unprocessed and processed whole documents on"
        // ss.ragService.core -> ss.ragService.backgroundTask "query processing tasks"
        // ss.ragService.core -> openaiapi "create embeddings for chunks of documents utilizing"
        // ss.ragService.core -> ss.ragService.vectorDB "store and retreive (similar) document chunks embeddings"
        // ss.ragService.core -> ss.ragService.metadataDB "store metadata information about documents stored in the VectorDB"

        // ss.ragService.core -> ss.interface "Sends messages when the processing status of uploaded documents has changed" "RESTApi"
        // ss.interface -> ss.react "Sends messages when the processing status of uploaded documents has changed to" "WSMessage"
        
        // github.webhook -> ss.ragService.githubDataService "Notifies about new commits" "POST Call"
        // ss.ragService.githubDataService -> github.core "retreives repository content from"
        // ss.ragService.githubDataService -> ss.ragService.core "updates outdate github repo data in"
        
        



        
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
        component ss.chatservice "chatServiceView"{
            include *
            exclude "element.type==Container -> element.type==Container"
            exclude "element.type==SoftwareSystem -> element.type==Container"
            exclude "element.type==Container -> element.type==SoftwareSystem"
            // autoLayout lr
        }

        // component ss.ragService "ragServiceView"{
        //     include *
        //     exclude "element.type==Container -> element.type==Container"
        //     exclude "element.type==SoftwareSystem -> element.type==Container"
        //     exclude "element.type==Container -> element.type==SoftwareSystem"
        //     // autoLayout lr
        // }

        component ss.customGPTService "customGPTServiceView"{
            include *
            exclude "element.type==Container -> element.type==Container"
            exclude "element.type==SoftwareSystem -> element.type==Container"
            exclude "element.type==Container -> element.type==SoftwareSystem"
            // autoLayout lr
        }

        dynamic ss "wsMessage"{
            title "client subscibes to websocketMsg"
            ss.react -> ss.interface "subscribes to websocketmessages"
        }

        // dynamic ss.ragService "uploadDocument"{
        //     title "upload document and start processing" 
        //     u -> ss.react "Uploads document to"
        //     ss.react -> ss.interface "sends document file via Post call to"
        //     ss.interface -> ss.ragService.core "send document to"
        //     ss.ragService.core -> ss.ragService.localFS "store original document in"
        //     ss.ragService.core -> ss.ragService.metadataDB "adds document infomation to and set status to uploaded"
        //     ss.ragService.core -> ss.ragService.backgroundTask "queue processing background task"
        //     ss.ragService.core -> ss.interface "notifies about the successful upload of the document"
        //     ss.interface -> ss.react "notifies about the successful upload of the document"
        // }

        // dynamic ss.ragService "processDocument"{
        //     title "uploaded document finished processing"
        //     ss.ragService.backgroundTask -> ss.ragService.core "trigger preprocessing of the document"
        //     ss.ragService.core -> ss.ragService.localFS "save preprocessed (whole) document"
        //     {
        //         {
        //             ss.ragService.core -> ss.ragService.metadataDB "update metadata information to note preprocessed document"
        //         }
        //         {
        //             ss.ragService.core -> openaiapi "create embeddings for created document chunks utilizing"
        //         }
        //     }
        //     ss.ragService.core -> ss.ragService.vectorDB "store embeddings in"
        //     ss.ragService.core -> ss.ragService.metadataDB "sets document status to available and updates other metadata information"
        //     ss.ragService.core -> ss.interface "notifies about the successful proccesing of the document"
        //     ss.interface -> ss.react "send notification about availability of the document to subscribed" "WSMessage"
        // }

        

        dynamic ss.customgptService "customGPTCreateOrEdit"{
            title "create or edit custom gpt"
            ss.react -> ss.interface "send customgpt form data to"
            ss.interface -> ss.customGPTService.core "forwad post call to"
            ss.customGPTService.core -> ss.customGPTService.db "save data and metadata in"
            ss.customGPTService.core ->  ss.interface "success response"
            ss.interface -> ss.react "success response"
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