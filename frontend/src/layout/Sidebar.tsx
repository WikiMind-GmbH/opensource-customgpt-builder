// Sidebar.tsx
import { NavLink, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { ChatService, ChatSummary } from "../client";
// import "./Sidebar.css";

export default function Sidebar() {
  const [summaries, setSummaries] = useState<ChatSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const location = useLocation();  // watch the router location

  useEffect(() => {
    async function loadSummaries() {
      try {
        const data = await ChatService.getChatSummaries();
        data.sort((a, b) => b.chat_id - a.chat_id);
        setSummaries(data);
      } catch (err: any) {
        setError(err.message ?? "Failed to load chats");
      }
    }
    loadSummaries();
  }, [location]);  // re-run on every navigation change

  return (
    <aside className="sidebar">
      <h2 className="title">Demo App</h2>
      <nav className="nav">
        <NavLink to="/createOrEditCustomGPT" className="navlink">
          Create custom GPTs
        </NavLink>
        <NavLink to="/displayCustomGPTs" className="navlink">
          Display custom GPTs
        </NavLink>
        <NavLink to="/" className="navlink">
          Create new chat
        </NavLink>

        <hr />

        {error && <div className="error">Error: {error}</div>}

        <ul className="chat-list">
          {summaries.map((s) => (
            <li key={s.chat_id}>
              <NavLink
                to={`/chatWindow/${s.chat_id}`}
                className="navlink chat-summary-link"
              >
                {s.chat_summary}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
