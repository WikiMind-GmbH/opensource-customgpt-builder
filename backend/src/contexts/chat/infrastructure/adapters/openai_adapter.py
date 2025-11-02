from openai import OpenAI
from src.contexts.chat.application.ports.llm_port import ErrorWhileCallingAPI, LlmPort, MessageDTOllm, NoAssistantResponse, RoleDTOllm
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion

from openai.types.chat.chat_completion_assistant_message_param import (
    ChatCompletionAssistantMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)


class OpenaiAdapter(LlmPort):
    def __init__(self, model_name:str) -> None:
        self.model_name:str = model_name

    
    def transform_message_dto_llm_to_message_openai_chat_completion(self, msg: MessageDTOllm) -> ChatCompletionMessageParam:
        match msg.role:
            case RoleDTOllm.assistant:
                return ChatCompletionAssistantMessageParam(
                    role="assistant", content=msg.imageUrlOrText
                )
            case RoleDTOllm.user:
                return ChatCompletionUserMessageParam(
                    role="user", content=msg.imageUrlOrText
                )
            case RoleDTOllm.system:
                return ChatCompletionSystemMessageParam(
                    role="system", content=msg.imageUrlOrText
                )

    def get_assistant_text_response(self, messages_excluding_sys_prompt: list[MessageDTOllm], cgpt_systemprompt: list[MessageDTOllm])->str:
        messages:list[ChatCompletionMessageParam] = []

        for msg in cgpt_systemprompt+messages_excluding_sys_prompt:
            messages.append(self.transform_message_dto_llm_to_message_openai_chat_completion(msg=msg))

        try:
            client = OpenAI()

            response: ChatCompletion = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            assistant_response: ChatCompletionMessage = response.choices[0].message
        except Exception as e:
            raise ErrorWhileCallingAPI(f"An error was raised when calling the openain endpoint with  {len(messages_excluding_sys_prompt)} Messages with the system prompt of length {len(cgpt_systemprompt)}") from e

        if assistant_response.tool_calls is not None:
            raise NotImplementedError
        if assistant_response.content is None:
            raise NoAssistantResponse(f"No response was given for the following {len(messages_excluding_sys_prompt)} Messages with the system prompt of length {len(cgpt_systemprompt)}")
        
        return assistant_response.content #ToDo: extend in future, especially with tool_calls