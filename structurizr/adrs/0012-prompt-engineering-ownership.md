# Who owns sysprompt generation
Date: 2025-08-04

## Status

OPEN    

## Context

We want to have nice decoupled contexts. The question is: who is generating the system prompt.   
For our customgpts, we want to construct a system prompt from its properties (i.e. tone, name, instructions, etc).   
We could either let the chat context retreive all properties of a specific customGPT via an adapter and construct the system prompt in the chat context, or we retreive from the adapter a system prompt instead.   

Other considerations will be how we incorperate tool calling information as well.    
As we wanted to (also) bind the ability to function call to the customgpts, having them inclueded in the system prompt of the customGPT seems reasonable as well.    
This could lead to complications if we want to use tool calls outside of cgpts.    
However, we could have the return of the cgpt port be one of many inputs to determine what tool calls to make available to the assistant.



Additionally, **we will need to make sure that our sysprompt is up-to-date.**
If we change something in our cgpt, the system prompt it will create is different.    
So we can not call the cgpt adapter only once per conversation creation and save its output.

Now we could either always call the adapter and retreive the system prompt per each call to the llm or have another solution maybe with redis pub-sub, where we keep the sysprompt up-to-date. But this might also be ugly coupling.

We could do everything in the orchestration layer and llmAdapter.
Retreive possible tools, retreive cgpt sysprompt, etc etc

Inspiration GPT Idea of what could be passed to the llmadapter from the service layer:
```
PromptBundle = {
  system: list[Message],      # from PromptProvider(s)
  tools: list[ToolSpec],      # from ToolProvider(s)
  seed:  list[Message],       # optional starter/user/assistant msgs
  context: list[Message],     # from ContextProvider(s)
  meta: dict[str, Any],       # free-form extensions, version tags
}
```

## Decision

We will let the customgpt port return a system prompt. In this way the responisbilities for cgpt is isolated in its context. No need to change the port if new properties are added to the cgpt context if it returns a system prompt.    
Also, the cgpt context is responsible for everything related to cgpts. Which properties it has, 
In this way, we decouple the contexts.   

Addi

Still, how tool calling will be implemented is still open.


## Consequences

For now: sysprompt will be passed by the 
Once tool calling and the rag system are researched