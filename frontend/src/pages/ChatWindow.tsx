import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import "./ChatWindow.css";
import { List } from "lodash";
import {
  AssistantMessage,
  ChatHistory,
  ChatCommandsService,
  ChatQueriesService,
  CustomGpTsQueriesService,
  CustomGPTInfosSchema,
  RoleQuery,
  SimplifiedMessageQueries,
  NewChatRequest,
  ContinueChatRequest,
} from "../client";
import { ChatLocationState } from "../interfaces/interfaces";

export default function ChatWindow() {
  /* 1 ▸ read optional id from URL  e.g.  /chatWindow/123 */
  const { conversationIdOrUndefinedfNewConversation } = useParams<{
    conversationIdOrUndefinedfNewConversation?: string;
  }>();
  
  const location = useLocation() as { state: ChatLocationState };

  const [gptIdOrNull, setGptId] = useState<string | null>(() =>
  location.state?.gptIdOrNullIfDefault ?? null
);

  // const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /* 2 ▸ local component state */
  const [messages, setMessages] = useState<SimplifiedMessageQueries[]>([]);
  const [input, setInput] = useState<string>("");
  const [currentGptName, setCurrentGptName] = useState<string>("GPT");
  const navigate = useNavigate();

  async function loadChatContentIfExisting() {
    if (conversationIdOrUndefinedfNewConversation !== undefined)
      try {
        const conversation: ChatHistory = await ChatQueriesService.chatHistoryById(
          conversationIdOrUndefinedfNewConversation
        );
        setMessages(conversation.messages);
        setGptId(conversation.custom_gpt_id)
      } catch (err: unknown) {
        setError((err as Error).message);
      } finally {
        // setLoading(false);
      }
  }

  async function setNameOfGPT() {
    if (gptIdOrNull) {
      try {
        const gptInfos: CustomGPTInfosSchema =
          await CustomGpTsQueriesService.getCustomGptInfos(gptIdOrNull);
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
    // every time the convo‐ID changes...
    if (conversationIdOrUndefinedfNewConversation === undefined) {
      // we’re back at “new” → reset
      setMessages([]);
      setInput("");
    } else {
      // if you want, you could also reload existing when ID appears
      loadChatContentIfExisting();
    }
  }, [conversationIdOrUndefinedfNewConversation]);

  useEffect(() => {
    setNameOfGPT();
  }, [gptIdOrNull]);

      

  async function handleSend() {
    if (!input.trim()) return;

    // push user message
    setMessages((prev) => [...prev, { role: RoleQuery.USER, message: input }]);
    setInput("");


  const req: ContinueChatRequest | NewChatRequest =
  conversationIdOrUndefinedfNewConversation !== undefined
    ? {
        request_message: input,
        conversation_id: conversationIdOrUndefinedfNewConversation,
      }
    : {
        request_message: input,
        custom_gpt_id: gptIdOrNull,
      };


    const response: AssistantMessage = await ChatCommandsService.sendUserMessage(req);
    const response_text: string = response.response_message.message;
    const convId = response.conversation_id;
    if (conversationIdOrUndefinedfNewConversation !== undefined) {
      setMessages((prev) => [
        ...prev,
        { role: RoleQuery.ASSISTANT, message: response_text },
      ]);
    } else {
      navigate(`/chatWindow/${convId}`, {
        state: { gptIdOrNullIfDefault: gptIdOrNull },
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
        {currentGptName}
      </h2>

      <div className="chat-messages">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`chat-msg ${m.role === RoleQuery.USER ? "right" : "left"}`}
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
