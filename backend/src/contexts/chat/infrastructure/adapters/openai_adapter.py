from src.contexts.chat.application.mappers import transform_message_domain_to_message_openai_chat_completion
from src.contexts.chat.domain.models import Message, Role
from openai import OpenAI
from src.contexts.chat.application.ports.llm_port import ErrorWhileCallingAPI, LlmPort, NoAssistantResponse
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion


class OpenaiAdapter(LlmPort):
    def __init__(self, model_name:str) -> None:
        self.model_name:str = model_name
    def get_assistant_response(self, messages_excluding_sys_prompt: list[Message], cgpt_systemprompt: list[Message])->str:
        messages:list[ChatCompletionMessageParam] = []

        for msg in cgpt_systemprompt+messages_excluding_sys_prompt:
            messages.append(transform_message_domain_to_message_openai_chat_completion(msg=msg))

        try:
            client = OpenAI()

            response: ChatCompletion = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            assistant_response: ChatCompletionMessage = response.choices[0].message
        except:
            raise ErrorWhileCallingAPI

        if assistant_response.tool_calls is not None:
            raise NotImplementedError
        if assistant_response.content is None:
            raise NoAssistantResponse
        
        return assistant_response.content #ToDo: extend in future, especially with tool_calls