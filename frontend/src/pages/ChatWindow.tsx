import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import "./ChatWindow.css";
import { List } from "lodash";
import {
  AssistantMessage,
  ChatHistory,
  ChatService,
  CustomGpTsService,
  ExistingCustomGPT,
  Role,
  SimplifiedMessage,
  UserMessageRequest,
} from "../client";

export default function ChatWindow() {
  /* 1 ▸ read optional id from URL  e.g.  /chatWindow/123 */
  const { conversationIdOrUndefinedfNewConversation }= useParams<{
    conversationIdOrUndefinedfNewConversation?: string;
  }>();
  const { state } = useLocation();
  const gptIdOrNullIfDefault =
    (state as { gptIdOrNullIfDefault?: number } | null)?.gptIdOrNullIfDefault ??
    null; // id null will be default gpt version

  // const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /* 2 ▸ local component state */
  const [messages, setMessages] = useState<SimplifiedMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [currentGptName, setCurrentGptName] = useState<string | null>(null);
  const navigate = useNavigate();

  async function loadChatContentIfExisting() {
    if (conversationIdOrUndefinedfNewConversation !== undefined)
      try {
        const conversation: ChatHistory = await ChatService.getChatHistoryById(
          Number(conversationIdOrUndefinedfNewConversation)
        );
        setMessages(conversation.messages);
      } catch (err: unknown) {
        setError((err as Error).message);
      } finally {
        // setLoading(false);
      }
  }

  async function setNameOfGPT() {
    if (gptIdOrNullIfDefault !== null) {
      try {
        const gptInfos: ExistingCustomGPT =
          await CustomGpTsService.getCustomGptInfos(gptIdOrNullIfDefault);
        setCurrentGptName(gptInfos.custom_gpt_name);
      } catch (err: unknown) {
        setError((err as Error).message);
      } finally {
        // setLoading(false);
      }
    } else {
      setCurrentGptName("Default GPT");
      // setLoading(false);
    }
  }

  useEffect(() => {
    loadChatContentIfExisting();
    setNameOfGPT();
  }, []);

  async function handleSend() {
    if (!input.trim()) return;

    // push user message
    setMessages((prev) => [...prev, { role: Role.USER, message: input }]);
    setInput("");
    const req: UserMessageRequest = {
      conversation_id:
        conversationIdOrUndefinedfNewConversation !== undefined
          ? Number(conversationIdOrUndefinedfNewConversation)
          : null,
      request_message: { role: Role.USER, message: input },
      custom_gpt_id: gptIdOrNullIfDefault,
    };
    const response: AssistantMessage = await ChatService.sendUserMessage(req);
    const response_text: string = response.response_message.message;
    const convId = response.conversation_id;
    if (conversationIdOrUndefinedfNewConversation !== undefined) {
      setMessages((prev) => [
        ...prev,
        { role: Role.ASSISTANT, message: response_text },
      ]);
    } else {
      navigate(`/chatWindow/:${conversationIdOrUndefinedfNewConversation}`, {
        state: { gptIdOrNullIfDefault: gptIdOrNullIfDefault },
      });
    }

    // Check if currently response_text conversationIdOrUndefinedfNewConversation is null then navigate, otherwise nothing
  }

  /* 4 ▸ UI */

  // if (loading) return <p className="center">Loading…</p>;
  if (error) return <p className="center">Error: {error}</p>;
  return (
    <div className="chat-root">
      <h2 className="chat-title">
        {gptIdOrNullIfDefault !== null
          ? `${currentGptName}`
          : "Vanilla ChatGPT"}
      </h2>

      <div className="chat-messages">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`chat-msg ${m.role === Role.USER ? "right" : "left"}`}
          >
            {m.message}
          </div>
        ))}
      </div>

      <div className="chat-input-row">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message…"
          className="chat-input"
          rows={2}
        />
        <button onClick={handleSend} className="chat-send-btn">
          Send
        </button>
      </div>
    </div>
  );
}
