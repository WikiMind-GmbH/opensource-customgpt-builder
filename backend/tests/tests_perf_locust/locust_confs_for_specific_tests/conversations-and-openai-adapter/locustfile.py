# Structure of test-suit in future https://docs.locust.io/en/stable/writing-a-locustfile.html#how-to-structure-your-test-code
import logging
import os
import random
import time
import uuid
from enum import StrEnum

from locust import (
    HttpUser,
    between,  # pyright: ignore [reportUnknownVariableType] | wait_time between is locust internal only, never referenced besides this declaration
    task,
)
from pydantic import BaseModel, TypeAdapter

logger = logging.getLogger(__name__)


# temporary solution: locust decoupled from backend -> manually copy dto types :(
# -----------------------------------------------------
class ChatSummary(BaseModel):
    chat_id: str
    chat_summary: str


class CustomGPTOverviewSchema(BaseModel):
    custom_gpt_id: str
    custom_gpt_name: str


class RoleCmd(StrEnum):
    user = "user"
    assistant = "assistant"


class SimplifiedMessageCmd(BaseModel):
    role: RoleCmd
    message: str


class AssistantMessage(BaseModel):
    conversation_id: str
    response_message: SimplifiedMessageCmd


class NewChatRequest(BaseModel):
    request_message: str
    custom_gpt_id: str | None


class ContinueChatRequest(BaseModel):
    request_message: str
    conversation_id: str


UserMessageRequest = NewChatRequest | ContinueChatRequest
# -----------------------------------------------------


def require_env_locust(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DEBUG_MODE_LOCUST: bool = require_env_locust("DEBUG_MODE_LOCUST").lower() == "true"
if DEBUG_MODE_LOCUST:
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))  # Debugger listens on port 5678
    debugpy.wait_for_client()


# *weight*: weight 3 is executed/created 3 times as often as weight 1
class CgptCreatorUser(HttpUser):
    weight = 0

    wait_time = between(10, 15)  # pyright: ignore [reportUnknownVariableType] | wait_time is locust internal only, never referenced besides this declaration
    host = require_env_locust("LOCUST_DESTINATION")

    def on_start(self) -> None:
        user = require_env_locust("LOCUST_BASIC_AUTH_USER")
        pwd = require_env_locust("LOCUST_BASIC_AUTH_PASSWORD")
        self.client.auth = (user, pwd)

    def create_instruction(self):
        if random.randint(1, 20) == 1:
            cgpt_instructions = f"instructions-{uuid.uuid4()}" + ("x" * 2000)
        else:
            cgpt_instructions = f"instructions-{uuid.uuid4()}"
        return cgpt_instructions

    @task(2)
    def create_and_retreive(self):
        cgpt_name = f"gpt-{uuid.uuid4()}"
        cgpt_description = f"description-{uuid.uuid4()}"
        cgpt_instructions = self.create_instruction()

        payload = {
            "custom_gpt_name": cgpt_name,
            "custom_gpt_description": cgpt_description,
            "custom_gpt_instructions": cgpt_instructions,
        }

        # create cgpt + get cgpt_id from response.resource_id
        with (
            self.client.post(
                "/customgpts/create-custom-gpt",
                json=payload,
                catch_response=True,
                name="/customgpts/create-custom-gpt",  # without this, each base+query url gets its own metrics/logs
            ) as resp
        ):
            if resp.status_code != 200:
                resp.failure(
                    f"Unexpected status {resp.status_code}: {resp.text}"
                )  # maybe due to the high load errors occur that are not caught in the functional tests -> with resp.failure, we let locust know to mark the test as failure
                return

            try:
                body = resp.json()
            except Exception:
                resp.failure(f"Invalid JSON: {resp.text}")
                return

            cgpt_id = body.get("resource_id")
            if not isinstance(cgpt_id, str) or not cgpt_id:
                resp.failure(f"Missing/invalid resource_id: {body}")
                return

        # retrieve cgpt infos + check for 200 + name match (only)
        with self.client.get(
            "/customgpts/get-custom-gpt-infos",
            params={"custom_gpt_id": cgpt_id},
            catch_response=True,
            name="/customgpts/get-custom-gpt-infos",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}: {resp.text}")
                return

            try:
                infos = resp.json()
            except Exception:
                resp.failure(f"Invalid JSON: {resp.text}")
                return

            if infos.get("custom_gpt_name") != cgpt_name:
                resp.failure(
                    f"Name mismatch: expected {cgpt_name}, got {infos.get('custom_gpt_name')}"
                )

    @task(1)
    def retreive_summaries_edit_one_cgpt(self):
        # retrieve (possibly empty) list of summaries (overviews)
        with self.client.get(
            "/customgpts/retreive-all-custom-gpts",
            catch_response=True,
            name="/customgpts/retreive-all-custom-gpts",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}: {resp.text}")
                return

            try:
                all_gpts = resp.json()
            except Exception:
                resp.failure(f"Invalid JSON: {resp.text}")
                return

            if not isinstance(all_gpts, list):
                resp.failure(f"Expected list, got {type(all_gpts)}: {all_gpts}")
                return

            if len(all_gpts) == 0:
                return

            try:
                chosen: CustomGPTOverviewSchema = (
                    CustomGPTOverviewSchema.model_validate(random.choice(all_gpts))
                )
            except Exception:
                resp.failure("List items are malformed")
                return

        cgpt_id = chosen.custom_gpt_id
        payload = {
            "custom_gpt_id": cgpt_id,
            "custom_gpt_name": f"gpt-{uuid.uuid4()}",
            "custom_gpt_description": f"description-{uuid.uuid4()}",
            "custom_gpt_instructions": f"instructions-{uuid.uuid4()}",
        }

        with self.client.post(
            "/customgpts/edit-custom-gpt",
            json=payload,
            catch_response=True,
            name="/customgpts/edit-custom-gpt",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}: {resp.text}")


class ChatUser(HttpUser):
    host = require_env_locust("LOCUST_DESTINATION")
    wait_time = between(10, 15)  # pyright: ignore [reportUnknownVariableType] | wait_time is locust internal only, never referenced besides this declaration

    def on_start(self) -> None:
        user = require_env_locust("LOCUST_BASIC_AUTH_USER")
        pwd = require_env_locust("LOCUST_BASIC_AUTH_PASSWORD")
        self.client.auth = (user, pwd)

    @task(1)
    def create_new_chat(self):
        new_chat_req: NewChatRequest = NewChatRequest(
            request_message="Hello", custom_gpt_id=None
        )
        with self.client.post(
            "/chat/send-user-message",
            json=new_chat_req.model_dump(mode="json"),
            name="POST /chat/send-user-message (new)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}: {resp.text}")
                return

            try:
                body = resp.json()
            except Exception:
                resp.failure(f"Invalid JSON: {resp.text}")
                return

            if not isinstance(body.get("conversation_id"), str) or not body.get(
                "conversation_id"
            ):
                resp.failure(f"Missing/invalid conversation_id: {body}")
                return

    @task(2)
    def look_up_chats(self):
        with self.client.get(
            "/chat/get-chat-summaries",
            name="GET /chat/get-chat-summaries",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}: {resp.text}")
                return

            try:
                summaries = resp.json()
            except Exception:
                resp.failure(f"Invalid JSON: {resp.text}")
                return

            if not isinstance(summaries, list):
                resp.failure(f"Expected list, got {type(summaries)}: {summaries}")
                return
            if len(summaries) == 0:
                return
            try:
                random.sample(summaries, k=min(3, len(summaries)))
                three_random_chats: list[ChatSummary] = TypeAdapter(
                    list[ChatSummary]
                ).validate_python(random.sample(summaries, k=min(3, len(summaries))))
            except Exception:
                resp.failure("Chatsummary response objects malformed")
                return

        for chat in three_random_chats:
            chat_id = chat.chat_id

            with self.client.get(
                "/chat/chat-history-by-id",
                params={"chat_id": chat_id},
                name="GET /chat/chat-history-by-id",
                catch_response=True,
            ) as resp:
                if resp.status_code != 200:
                    resp.failure(f"Unexpected status {resp.status_code}: {resp.text}")
                    return

                try:
                    _history = resp.json()
                except Exception:
                    resp.failure(f"Invalid JSON: {resp.text}")
                    return

    @task(1)
    def continue_chat(self):
        with self.client.get(
            "/chat/get-chat-summaries",
            name="GET /chat/get-chat-summaries",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}: {resp.text}")
                return

            try:
                summaries = resp.json()
            except Exception:
                resp.failure(f"Invalid JSON: {resp.text}")
                return

            if not isinstance(summaries, list):
                resp.failure(f"Expected list, got {type(summaries)}: {summaries}")
                return
            if len(summaries) == 0:
                return
            try:
                chat: ChatSummary = ChatSummary.model_validate(random.choice(summaries))
                chat_id = chat.chat_id
            except Exception:
                resp.failure("Chatsummary response objects malformed")
                return

        for _ in range(7):
            time.sleep(8)
            payload = {
                "request_message": "Please create a small poem with approx. 100 words",
                "conversation_id": chat_id,
            }

            with self.client.post(
                "/chat/send-user-message",
                json=payload,
                name="POST /chat/send-user-message (continue)",
                catch_response=True,
            ) as resp:
                if resp.status_code != 200:
                    resp.failure(f"Unexpected status {resp.status_code}: {resp.text}")
                    return

                try:
                    body = resp.json()
                    assistant_response: AssistantMessage = (
                        AssistantMessage.model_validate(body)
                    )
                except Exception:
                    resp.failure(f"Invalid JSON: {resp.text}")
                    return

                msg = assistant_response.response_message.message
                if len(msg) == 0:
                    resp.failure("Empty assistant message")
                    return
