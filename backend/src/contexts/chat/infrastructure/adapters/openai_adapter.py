from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_assistant_message_param import (
    ChatCompletionAssistantMessageParam,
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_system_message_param import (
    ChatCompletionSystemMessageParam,
)
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)

from src.contexts.chat.application.ports.llm_port import (
    ErrorWhileCallingAPI,
    LlmPort,
    MessageDTOllm,
    NoAssistantResponse,
    RoleDTOllm,
)


class OpenaiAdapter(LlmPort):
    def __init__(self, model_name: str) -> None:
        self.model_name: str = model_name
        self.client: OpenAI = OpenAI()

    def transform_message_dto_llm_to_message_openai_chat_completion(
        self, msg: MessageDTOllm
    ) -> ChatCompletionMessageParam:
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

    def get_assistant_text_response(
        self,
        messages_dto: list[MessageDTOllm],
    ) -> str:
        messages_openai_chat_completion: list[ChatCompletionMessageParam] = []

        for msg in messages_dto:
            messages_openai_chat_completion.append(
                self.transform_message_dto_llm_to_message_openai_chat_completion(
                    msg=msg
                )
            )

        try:
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages_openai_chat_completion,
            )
            assistant_response: ChatCompletionMessage = response.choices[0].message
        except Exception as e:
            raise ErrorWhileCallingAPI(
                f"An error was raised when calling the openain endpoint with  {len(messages_openai_chat_completion)} Messages"
            ) from e

        if assistant_response.tool_calls is not None:
            raise NotImplementedError
        if assistant_response.content is None:
            raise NoAssistantResponse(
                f"No response was given for the following {len(messages_openai_chat_completion)} Messages"
            )

        return (
            assistant_response.content
        )  # ToDo: extend in future, especially with tool_calls
