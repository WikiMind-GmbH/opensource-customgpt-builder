import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./DisplayCustomGPTs.css";

/* --- DTO type that matches backend response ------------------ */
type CustomGptInfo = {
  customGptId: number;
  customGptName: string;
};
/* ------------------------------------------------------------- */

export default function DisplayCustomGPTs() {
  const [gpts, setGpts] = useState<CustomGptInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  /* fetch list once */
  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/custom-gpts");  // ⬅️ adjust endpoint
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: CustomGptInfo[] = await res.json();
        setGpts(data);
      } catch (err: unknown) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleDelete(id: number) {
  if (!confirm("Delete this GPT?")) return;

  try {
    const res = await fetch(`/api/custom-gpts/${id}`, { method: "DELETE" });

    if (!res.ok) {
      /* backend replied 4xx/5xx → show message and keep the item */
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail ?? `HTTP ${res.status}`);
    }

    /* success → update UI */
    setGpts((prev) => prev.filter((g) => g.customGptId !== id));
  } catch (err: unknown) {
    alert(`Delete failed: ${(err as Error).message}`);
  }
}

  if (loading) return <p className="center">Loading…</p>;
  if (error)   return <p className="center">Error: {error}</p>;

  return (
    <div className="gpt-list-root">
      <h2 className="header">My GPTs</h2>

      {gpts.length === 0 && (
        <p className="center">You have no custom GPTs yet.</p>
      )}

      {gpts.map(({ customGptId, customGptName }) => (
        <div key={customGptId} className="gpt-row">
          <span className="gpt-name">{customGptName}</span>

          <div className="btn-group">
            <button
              type="button"
              onClick={() => navigate("/chatWindow", { state: { gptId: customGptId } })}
              className="btn primary"
            >
                Chat
            </button>
            <button
              type="button"
              onClick={() => navigate(`/createCustomGPTs/${customGptId}`)}
              className="btn secondary"
            >
              Edit
            </button>
            <button
              type="button"
              onClick={() => handleDelete(customGptId)}
              className="btn danger"
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
