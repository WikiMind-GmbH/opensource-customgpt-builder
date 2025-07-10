import { useLocation, useParams } from "react-router-dom";
import { useState } from "react";
import "./ChatWindow.css";
import { List } from "lodash";

/* --- domain types -------------------------------------------------------- */
export enum Role {
  USER = "user",
  CHATBOT_RESPONSE_FOR_USER = "chatbotResponseForUser",
}

export interface ChatMessage {
  role: Role;
  text: string;
}
/* ------------------------------------------------------------------------ */

export default function ChatWindow() {
  /* 1 ▸ read optional id from URL  e.g.  /chatWindow/123 */
  const { idOfChat } = useParams<{ idOfChat?: string }>();
  const { state } = useLocation();
  const gptId = (state as { gptId?: number } | null)?.gptId ?? 0; // id 0 will be default gpt version
  /* 2 ▸ local component state */
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");

  /* 3 ▸ send handler */
  // function getAndSetMessages(){
  //   if(idOfChat==null){
  //     alert("Should only be");
  //   }
  //   const messages: List[ChatMessage] = await getMessagesById(idOfChat)
  // }

  function handleSend() {
    if (!input.trim()) return;

    // push user message
    setMessages((prev) => [...prev, { role: Role.USER, text: input }]);
    setInput("");

    // TODO: replace with real backend / WebSocket call
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: Role.CHATBOT_RESPONSE_FOR_USER,
          text: `Echo: ${input}`,
        },
      ]);
    }, 500);
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
