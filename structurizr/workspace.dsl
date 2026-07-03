workspace "CustomGPT" "Use Chatgpt api with own customGPT implementation"{
    // this enables us to write ss.containername instead of just containername -
    !identifiers hierarchical 


    model {
        u = person "User" "A user of the system wanting to profit from customized llm chat functionality" "Person"
        ss = softwareSystem "Opensource CustomGPT builder"{
            react = container "Frontend" "A web app for chat with custom gpts and your data" "React + TS" "Web Browser"
            fastapiEntrypoint = container "FastapiEntrypoint" "Entrypoint into backend for frontend, imports all routers & exception handlers"
            chatContext = container "ChatContext" "Provides chat functionality. Handles prompt composition utilizing other contexts adapters"{
                orcherstrationLayer = component "Ochestration Layer" "provides use case functionality (create/continue conversation) by orchestrating domain and adapters"
                CommandsRouter = component "chatCommands Router" "API providing all commands"
                QueriesRouter = component "chatQueries Router" "API providing all queries"
                Domain = component "Chat Domain | ORM MAPPED" "provides conversation models, and functions like adding messages and composing the prompt | ORM mapped"

                uowAdapter = component "Conversation UOW Adapter" "Wraps db operations in a safe state way, only way to commit | returns orm mapped objects"
                repositoryAdapter = component "Conversation repo Adapter" "Create, add and delete conversations in DB. | returns orm mapped objects"
                llmAdapter = component "LLMAdapter" "Provides the functionality to query an llm for an assistent message, given a prompt(=list of messages), implementing the LLMPort"
                db = component "ConversationDB" "Stores the conversation histories and metadata of the conversation"{
                    tags "Database"
                    technology "PostgreSQL"
                }
                // Adapters providing for other contexts
                DeleteConvsWithCGPTAdapter = component "DeleteConvsWithCGPT Adapter" "provides function to delete all conversations associated with specific cgpt"
            }
            customgptContext = container "CustomGPTContext" "Stores and Serves basic CustomGPT information"{
                CommandsRouter = component "customgptCommands Router" "API providing all commands"
                QueriesRouter = component "customgptQueries Router" "API providing all queries"
                
                orcherstrationLayer = component "Ochestration Layer" "provides use case functionality (create/edit/delete customgpt) by orchestrating domain and adapters"
                Domain = component "CustomGPT Domain | ORM MAPPED" "provides CustomGPT model, no functions | ORM mapped"
                uowAdapter = component "Conversation UOW Adapter" "Wraps db operations in a safe state way, only way to commit | returns orm mapped objects"
                repositoryAdapter = component "Conversation repo Adapter" "Create, add and delete conversations in DB. | returns orm mapped objects"
                
                db = component "CustomGptDB" "Stores the information of the CustomGPTs"{
                    tags "Database"
                    technology "PostgreSQL"
                }

                // Adapters providing for other contexts
                cgptInfoAdapter = component "cgptInfoAdapter" "provides functionality to return instruction and name of a specific gpt, implementing a Port in the chatContext"
                cgpt_permission_adapter = component "cgpt_permission_adapter" "provides functionality to check if a user has access to a custom gpt (and if it exists) | Implementing Port of knowledge context"
            }
            knowledgeContext = container "knowledgeContext" "retrieve fitting document chunks and provide an api to manage data"{
                CommandsRouter = component "knowledgeContextCommands Router" "API providing all commands"
                QueriesRouter = component "knowledgeContextQueries Router" "API providing all queries"
                
                orcherstrationLayer = component "Ochestration Layer" "provides use case functionality (process files/retrieve relevant chunks/...) by orchestrating domain and adapters"
                Domain = component "Knowledge Domain" "core business logic: chunkking, retrieval stategies, models of chunks with metadata, files with metadata, etc  | ORM mapped"
                metadataUowAdapter = component "Metadb UOW Adapter" "Wraps db operations in a safe state way, only way to commit | returns orm mapped objects"
                metadataRepositoryAdapter = component "Metadb repo Adapter" "Create, add and delete conversations in DB. | returns orm mapped objects"
                metadataDB = component "MetadataDB" "Store relevant metadata per chunk, e.g. file_id, cgpt_ids, user, file_metadata, ..."{
                    tags "Database"
                    technology "Postgresql"
                }
                preProcessTextAlikesAdapter = component "Preprocess text alikes adapter" "Pre processes raw files mostyl containing text(word/pdf) to raw string |completely ignores images)"
                
                // ATTENTION: Do not outsource the core design decisions into the adapter. 
                // If we use advanced strategies like  multi query retrieval or auto-merging retriever, we do not want to hide this behind the adapter but integrate it into our domain/service layer as far as possible
                retreiveRelevantDocumentSnippetsAdapter = component "Relevant Doc snippets retreiver Adapter" "CORE FUNCTIONALITY retrieve and store chunks+embeddings; CORE: retrieval strategy"
                
                vectorstoreAdapter = component "vectorstoreAdapter" "Store and retreive chunks+embeddings+metadata(for filtering) ; uses domain model chunk with metadata + embedding for store"
                vectorDB = component "vectorDB" "Used to store text chunks with corresponding embedding and metadata"{
                    tags "Database"
                    technology "Qdrant"
                }

                fileStorageAdapterlocalFS = component "File storage adapter utilizing LocalFS" "Used to store non-processed and pre-processesed whole documents"
                fileSystem = component "Local File system" "Used as file storage for raw and pre-processed documents uploaded by user" {
                    tags LocalFS
                }

                textEmbeddingGenAdapter = component "TextEmbeddingGeneratorAdapter" "generates embeddings of strings"

                // backgroundTask = component "Background Task" "Queue tasks to continue directly after responding"
                // githubDataContext = component "githubDataContext" "Listens for notification updates from github and updates the corresponding data in the vectorDB"
            }
 
            !docs docs
            !adrs adrs
            
        }
        openaiapi = softwareSystem "OpenAIApi" "Pass conversation and retrieve assistant messages of OpenAI LLMs" "External System"
        openaiEmbeddingAPI = softwareSystem "OpenAI Embedding API" "Creates embeddings for text chunks" "External System"
        // github = softwareSystem "github" "Sends a Post message to all subscribers whenever a new commit was made" "External System" {
        //     webhook = container "githubWebhook" "Listens for new commits and sends Post call to specific url"
        //     api = container "GithubAPI" "Provides api for interacting with github repos, e.g. retrieving data"
        // }
        // TOP LEVEL (TO KEEP IT CLEAN)------------------------
        u -> ss.react "Chats with LLM, creates or uses CustomGPTs using" "RestAPI"
        ss.react -> ss.fastapiEntrypoint "creates, retrieves and chats with a llm or customGPTs, utilizing own files" "RESTApi"

        ss.fastapiEntrypoint -> ss.chatContext "provides its chat functionality (create/continue/get) by utilizing endpoints defined in"
        ss.fastapiEntrypoint -> ss.customGPTContext "provides its functionality to create/continue/get/delete customgpts by utilizing endpoints of"
        ss.fastapiEntrypoint -> ss.knowledgeContext "provides its functionality to upload documents and get infos on uploaded docs by utiliuzing the endpoints of"


        // CHAT CONTEXT AND ADAPTERS PROVIDING FOR IT-----------------------------
        ss.fastapiEntrypoint -> ss.chatContext.QueriesRouter "gets conversational data and other get request by utilizing the endpoints in the"
        ss.chatContext.QueriesRouter -> ss.chatContext.db "gets conversational data efficiently via direct sql queries to"
        ss.fastapiEntrypoint -> ss.chatContext.CommandsRouter "provides the functionality to to start or continue a conversation by utilizing the endpoints of the" 
        ss.chatContext.CommandsRouter -> ss.chatContext.orcherstrationLayer "provides its functionality by utilizing the"
        ss.chatContext.orcherstrationLayer -> ss.chatContext.uowAdapter "wraps in one transaction: create, store, delete, retrieve and change domain model objects"
        ss.chatContext.uowAdapter -> ss.chatContext.repositoryAdapter "provides its ability by calling functions and properties of"
        ss.chatContext.repositoryAdapter -> ss.chatContext.db "Utilizes sqlalchemy and rom mapping to"

        ss.chatContext.orcherstrationLayer -> ss.chatContext.domain "add messages and create prompt by utilizing the models and their functions of the"

        ss.chatContext.orcherstrationLayer -> ss.customgptContext.cgptInfoAdapter "gets plain description and name of specific customgpts (for prompt composition) from"

        // ss.chatContext.core -> ss.knowledgeContext.core "Sends text-snipet and gets relevant document chunks and their metadata from"
        ss.chatContext.orcherstrationLayer -> ss.chatContext.llmAdapter "sends list of messages to gets llm assistant response to"
        ss.chatContext.llmAdapter -> openaiapi "provides its llm functionality by utilizing" "RestAPI"
        ss.ChatContext.orcherstrationLayer -> ss.knowledgeContext.retreiveRelevantDocumentSnippetsAdapter "retrieve relevant file chunks to a passed text snippet"
        ss.chatContext.DeleteConvsWithCGPTAdapter -> ss.chatContext.uowAdapter "deletes chats by using the"
        //---------------------------------------------------------------------------------------------------------------------
        
        // CUSTOMGPT CONTEXT AND ADAPTERS PROVIDING FOR IT-----------------------------
        ss.fastapiEntrypoint -> ss.customGPTContext.QueriesRouter "gets conversational data and other get request by utilizing the endpoints in the"
        ss.customGPTContext.QueriesRouter -> ss.customGPTContext.db "gets customgpt data efficiently via direct sql queries to"
        ss.fastapiEntrypoint -> ss.customGPTContext.CommandsRouter "provides the functionality to to change or delete customgpts by utilizing endpoints of" 
        ss.customGPTContext.CommandsRouter -> ss.customGPTContext.orcherstrationLayer "provides its functionality by utilizing the service functions of"
        ss.customGPTContext.orcherstrationLayer -> ss.customGPTContext.uowAdapter "wraps in one transaction: create, store, delete, retrieve and change domain model objects"
        ss.customGPTContext.uowAdapter -> ss.customGPTContext.repositoryAdapter "provides its ability by calling functions and properties of"
        ss.customGPTContext.repositoryAdapter -> ss.customGPTContext.db "Utilizes sqlalchemy and rom mapping to"

        ss.customGPTContext.orcherstrationLayer -> ss.customGPTContext.domain "utilize the models of the"

        ss.customgptContext.orcherstrationLayer -> ss.chatContext.DeleteConvsWithCGPTAdapter "delete all conversations associated with a specific cgpt"

        ss.customgptContext.cgpt_permission_adapter -> ss.customGPTContext.db "use straight sql to check if user has access to specific cgpt"
        ss.customgptContext.cgptInfoAdapter -> ss.customGPTContext.uowAdapter "gets the description and name of a cgpt by using"
        // ss.customgptContext.core -> ss.customgptContext.db "Stores and retrieves CustomGPT information -including metadata- to and from" "SQLModel"
        //---------------------------------------------------------------------------------------------------------------------

        // KNOWLEDGE CONTEXT AND ADAPTERS PROVIDING FOR IT-----------------------------

        ss.fastapiEntrypoint -> ss.knowledgeContext.QueriesRouter "get file names and other info on stored documents by utiliuzing the endpoints of"
        
        // below: not possible if cgpt context adapter is needed to check permissions 
        // ss.knowledgeContext.QueriesRouter -> ss.knowledgeContext.metadataDB "gets metadata efficiently via direct sql queries to"
        // ss.knowledgeContext.QueriesRouter -> ss.knowledgeContext.fileStorageAdapterlocalFS "retrieve the original files from"

        ss.fastapiEntrypoint -> ss.knowledgeContext.CommandsRouter "provides the functionality to upload files by utilizing the endpoints of the" 
        ss.knowledgeContext.CommandsRouter -> ss.knowledgeContext.orcherstrationLayer "provides its functionality by utilizing the"
        ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "wraps in one transaction: create, store, delete, retrieve and change metadata"
        ss.knowledgeContext.metadataUowAdapter -> ss.knowledgeContext.metadataRepositoryAdapter "provides its ability by calling functions and properties of"
        ss.knowledgeContext.metadataRepositoryAdapter -> ss.knowledgeContext.metadataDB "Utilizes sqlalchemy and rom mapping to"

        ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.preProcessTextAlikesAdapter "pre-process text-like files to raw text"
        ss.knowledgeContext.retreiveRelevantDocumentSnippetsAdapter -> ss.knowledgeContext.orcherstrationLayer "calls retreival service function of"

        ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "get text chunk and file domain models with functions to chunk transformed text"
        ss.knowledgeContext.orcherstrationLayer -> ss.customGPTContext.cgpt_permission_adapter "check if user has access to cgpt"
        ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.fileStorageAdapterlocalFS "save and retreive documents"
        ss.knowledgeContext.fileStorageAdapterlocalFS -> ss.knowledgeContext.fileSystem "utilizes"
        ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.textEmbeddingGenAdapter "generates an embedding for a given text chunk"
        ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.vectorstoreAdapter "store embeddings and retreive close embeddings"
        ss.knowledgeContext.vectorstoreAdapter -> ss.knowledgeContext.vectorDB "utilizes as db" "Qdrant"
        ss.knowledgeContext.vectorstoreAdapter -> openaiEmbeddingAPI "utilizes as embedding generator" "RestAPI"
        
        //---------------------------------------------------------------------------------------------------------------------

        // ss.interface -> ss.knowledgeContext.core "Sends documents to process and embedd and retrieves relevant document chunks to a given text from"
        // ss.knowledgeContext.core -> ss.knowledgeContext.localFS "store unprocessed and processed whole documents on"
        // ss.knowledgeContext.core -> ss.knowledgeContext.backgroundTask "query processing tasks"
        // ss.knowledgeContext.core -> openaiapi "create embeddings for chunks of documents utilizing"
        // ss.knowledgeContext.core -> ss.knowledgeContext.vectorDB "store and retrieve (similar) document chunks embeddings"
        // ss.knowledgeContext.core -> ss.knowledgeContext.metadataDB "store metadata information about documents stored in the VectorDB"

        // ss.knowledgeContext.core -> ss.interface "Sends messages when the processing status of uploaded documents has changed" "RESTApi"
        // ss.interface -> ss.react "Sends messages when the processing status of uploaded documents has changed to" "WSMessage"
        
        // github.webhook -> ss.knowledgeContext.githubDataContext "Notifies about new commits" "POST Call"
        // ss.knowledgeContext.githubDataContext -> github.core "retrieves repository content from"
        // ss.knowledgeContext.githubDataContext -> ss.knowledgeContext.core "updates outdate github repo data in"
        
        



        
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
        component ss.chatContext "chatContextView"{
            include *
            exclude "element.type==Container -> element.type==Container"
            exclude "element.type==SoftwareSystem -> element.type==Container"
            exclude "element.type==Container -> element.type==SoftwareSystem"
            // autoLayout lr
        }

        component ss.knowledgeContext "knowledgeContextView"{
            include *
            exclude "element.type==Container -> element.type==Container"
            exclude "element.type==SoftwareSystem -> element.type==Container"
            exclude "element.type==Container -> element.type==SoftwareSystem"
            // autoLayout lr
        }

        component ss.customGPTContext "customGPTContextView"{
            include *
            exclude "element.type==Container -> element.type==Container"
            exclude "element.type==SoftwareSystem -> element.type==Container"
            exclude "element.type==Container -> element.type==SoftwareSystem"
            // autoLayout lr
        }

        // dynamic ss "wsMessage"{
        //     title "client subscibes to websocketMsg"
        //     ss.react -> ss.interface "subscribes to websocketmessages"
        // }
        dynamic ss.knowledgeContext "uploadAndPreprocessTextLikeDoc"{
            title "CHECK IN CODE: Upload and pre-process text like document (missing: retry logic for each ±Transaction)"
            u -> ss.react "Uploads document to"
            ss.react -> ss.fastapiEntrypoint "sends document file to"
            ss.fastapiEntrypoint -> ss.knowledgeContext.CommandsRouter "routes call to endpoint uploadTextLikeDoc of"
            ss.knowledgeContext.CommandsRouter -> ss.knowledgeContext.orcherstrationLayer "call service function $NAME of"
            ss.knowledgeContext.orcherstrationLayer -> ss.customGPTContext.cgpt_permission_adapter "assure that user has access to cgpt | IF NOT: THROW 404 error back to frontend"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "assure that the file type is supported (inferred from filename) | IF NOT: THROW 404 error back to frontend"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "TRANSACTION ONE: open UOW"
            // shouldn't we make local fs & vector store also a uow such that we can rollback i.e. delete?
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "Calculate hash based on file-type(inferred from filenam suffix) -> RETURN hash, byte content of file, file-type |IF UNSUPPORTED FILE TYPE: throw error back to frontend(domain error -orchstration level error mappers-> https error)"
            ss.knowledgeContext.metadataUowAdapter -> ss.knowledgeContext.metadataRepositoryAdapter "TRANSACTION ONE: check if file with this hash exists already"
         }

        dynamic ss.knowledgeContext "uploadAndPreprocessTextLikeDocHashDoesExist"{
            title "CHECK IN CODE: Upload and pre-process text like document |BRANCH: HASH DOES EXIST ALREADY (missing: retry logic for each ±Transaction)"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "TRANSACTION ONE: (If already exist) via model functions: add cgpt id to permission list of file; DONE"
        }
        dynamic ss.knowledgeContext "uploadAndPreprocessTextLikeDocHashDoesNotExist"{
            title "CHECK IN CODE: Upload and pre-process text like document |BRANCH: HASH DOES NOT EXIST YET (missing: retry logic for each ±Transaction)"
            ss.knowledgeContext.metadataUowAdapter -> ss.knowledgeContext.metadataRepositoryAdapter "TRANSACTION ONE: check if file with this hash exists already | DOES NOT"
            ss.knowledgeContext.metadataUowAdapter -> ss.knowledgeContext.metadataRepositoryAdapter "TRANSACTION ONE: create new file domain model( file_type, name used for init| id=uuid;)"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.fileStorageAdapterlocalFS "TRANSACTION ONE: Store raw unprocessed file (pass: uploadfile.id, bytes_content)"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "TRANSACTION ONE: via domain model object function: set status to raw_file_uploaded"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "TRANSACTION ONE: commit"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.CommandsRouter "retrurn http response upload succesfull, processing queued/ or finished if file already exist in db"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.preProcessTextAlikesAdapter "preprocess the raw document based on file_type, returns string | PASS: bytes_content, file_type" 
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "TRANSACTION TWO: open UOW"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "TRANSACTION TWO: change file domain model: preprocessed text= raw string, [change status to preprocessed(?)]" 
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "TRANSACTION TWO: commit"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "TRANSACTION THREE: open UOW"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "TRANSACTION THREE: create all document chunks via model fnx | document chunks are domain model; uuid, ref fil, raw_text, include metadata properties used for retrieval logic"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "TRANSACTION THREE: update document file domain model to fully chunked"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "TRANSACTION THREE: commit (if any errors had occured -rollback all changes; need to fully rechunk)"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.textEmbeddingGenAdapter "LOOP TILL ALL CHUNKS EMBEDDED OF DOC: create embedding for text chunk"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.vectorstoreAdapter "LOOP TILL ALL CHUNKS EMBEDDED OF DOC: pass embedding with chunk domain model incl. metadata properties"
            ss.knowledgeContext.vectorstoreAdapter -> ss.knowledgeContext.vectorDB "LOOP TILL ALL CHUNKS EMBEDDED OF DOC: store embedding, use id, metadata fields as json"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "LOOP TILL ALL CHUNKS EMBEDDED OF DOC: Open uow"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.domain "LOOP TILL ALL CHUNKS EMBEDDED OF DOC: change chunk status to: embedded"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.metadataUowAdapter "LOOP TILL ALL CHUNKS EMBEDDED OF DOC: commit"
            // send to client/ update job to  embedded
        }
        
        dynamic ss.knowledgeContext "retreiveDocumentChunksUnsuccesfull"{
            title "CHECK IN CODE: retreive relevant chunks unsuccessful| missing: retry logic for each ±Transaction"
            ss.chatContext.orcherstrationLayer -> ss.knowledgeContext.retreiveRelevantDocumentSnippetsAdapter "sends text snippet + gpt id to"
            ss.knowledgeContext.orcherstrationLayer -> ss.customGPTContext.cgpt_permission_adapter "check if user has access to this cgpt -> does not"
            ss.knowledgeContext.orcherstrationLayer -> ss.knowledgeContext.CommandsRouter "Return http error 404 not found"
        }


        // dynamic ss.knowledgeContext "uploadDocument"{
        //     title "upload document and start processing" 
        //     ss.interface -> ss.knowledgeContext.core "send document to"
        //     ss.knowledgeContext.core -> ss.knowledgeContext.localFS "store original document in"
        //     ss.knowledgeContext.core -> ss.knowledgeContext.metadataDB "adds document infomation to and set status to uploaded"
        //     ss.knowledgeContext.core -> ss.knowledgeContext.backgroundTask "queue processing background task"
        //     ss.knowledgeContext.core -> ss.interface "notifies about the successful upload of the document"
        //     ss.interface -> ss.react "notifies about the successful upload of the document"
        // }

        // dynamic ss.knowledgeContext "processDocument"{
        //     title "uploaded document finished processing"
        //     ss.knowledgeContext.backgroundTask -> ss.knowledgeContext.core "trigger preprocessing of the document"
        //     ss.knowledgeContext.core -> ss.knowledgeContext.localFS "save preprocessed (whole) document"
        //     {
        //         {
        //             ss.knowledgeContext.core -> ss.knowledgeContext.metadataDB "update metadata information to note preprocessed document"
        //         }
        //         {
        //             ss.knowledgeContext.core -> openaiapi "create embeddings for created document chunks utilizing"
        //         }
        //     }
        //     ss.knowledgeContext.core -> ss.knowledgeContext.vectorDB "store embeddings in"
        //     ss.knowledgeContext.core -> ss.knowledgeContext.metadataDB "sets document status to available and updates other metadata information"
        //     ss.knowledgeContext.core -> ss.interface "notifies about the successful proccesing of the document"
        //     ss.interface -> ss.react "send notification about availability of the document to subscribed" "WSMessage"
        // }

        

        // dynamic ss.customgptContext "customGPTCreateOrEdit"{
        //     title "create or edit custom gpt"
        //     ss.react -> ss.fastapiEntrypoint "send customgpt form data to"
        //     ss.fastapiEntrypoint -> ss.customgptContext.CommandsRouter "utilizes router"
        //     ss.interface -> ss.customGPTContext.core "forwad post call to"
        //     ss.customGPTContext.core -> ss.customGPTContext.db "save data and metadata in"
        //     ss.customGPTContext.core ->  ss.interface "success response"
        //     ss.interface -> ss.react "success response"
        // }


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
            element "LocalFS"{
                shape Folder
            }
        }
    }
}