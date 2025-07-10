import { useLocation, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import "./ChatWindow.css";
import { List } from "lodash";
import { ChatHistory, ChatHistoryService, CustomGptService, ExistingCustomGPT, Role, SimplifiedMessage } from "../client";


export default function ChatWindow() {
  /* 1 ▸ read optional id from URL  e.g.  /chatWindow/123 */
  const { idOfChat } = useParams<{ idOfChat?: string }>();
  const { state } = useLocation();
  const gptIdOrNullIfDefault = (state as { gptIdOrNullIfDefault?: number } | null)?.gptIdOrNullIfDefault ?? null; // id null will be default gpt version
  const conversationIdOrNullIfNewConversation = (state as { conversationIdOrNullIfNewConversation?: number } | null)?.conversationIdOrNullIfNewConversation ?? null; // id 0 will be default gpt version
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /* 2 ▸ local component state */
  const [messages, setMessages] = useState<SimplifiedMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [currentGpt, setCurrentGpt] = useState<number | null>(null)
  const [currentGptName, setCurrentGptName] = useState<string | null>(null)


  async function loadChatContentIfExisting() {
        if(conversationIdOrNullIfNewConversation)
        try {
          const conversation: ChatHistory = await ChatHistoryService.getChatHistoryById(conversationIdOrNullIfNewConversation);
          setMessages(conversation.messages);
        } catch (err: unknown) {
          setError((err as Error).message);
        } finally {
          setLoading(false);
        }
      }
  
  async function setNameOfGPT() {
        if(gptIdOrNullIfDefault){
          try {
              const all_gpts: ExistingCustomGPT[] = await CustomGptService.dispalyAllCustomGpTs()
              const name =
                all_gpts.find(
                  ({ custom_gpt_id }) => custom_gpt_id === gptIdOrNullIfDefault,
                )?.custom_gpt_name ?? "Unknown GPT"; // fallback
              setCurrentGptName(name);
            } catch (err: unknown) {
              setError((err as Error).message);
            } finally {
              setLoading(false);
          }
        }
        setCurrentGptName("Default GPT")
        
      }



  useEffect(() => {
      loadChatContentIfExisting();
      setNameOfGPT();
    }, []);
  

  function handleSend() {
    if (!input.trim()) return;

    // push user message
    setMessages((prev) => [...prev, { role: Role.USER, message: input }]);
    setInput("");

    // TODO: replace with real backend / WebSocket call
    const res = 
  }

  /* 4 ▸ UI */
  return (
    <div className="chat-root">
      <h2 className="chat-title">
        {idOfChat ? `Conversation #${idOfChat}` : "New Conversation"}
      </h2>

      <div className="chat-messages">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`chat-msg ${m.role === Role.USER ? "right" : "left"}`}
          >
            {m.text}
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
