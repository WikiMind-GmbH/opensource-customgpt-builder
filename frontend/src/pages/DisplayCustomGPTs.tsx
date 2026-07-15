import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./DisplayCustomGPTs.css";
import {
  deleteCustomGpt,
  retreiveAllCustomGpts,
} from "../client";
import type { CustomGptOverviewSchema } from "../client";
import { CustomGptInfo } from "../interfaces/interfaces";

export default function DisplayCustomGPTs() {
  const [gpts, setGpts] = useState<CustomGptInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  /* fetch list once */
  useEffect(() => {
    async function load() {
      try {
        const { data: existingGPTList }: { data: CustomGptOverviewSchema[] } =
          await retreiveAllCustomGpts();
        const customGptInfos: CustomGptInfo[] = existingGPTList.map(
          ({
            custom_gpt_id: customgptIdOrNullIfDefault,
            custom_gpt_name: customGptName,
          }) => ({
            customgptIdOrNullIfDefault,
            customGptName,
          })
        );
        setGpts(customGptInfos);
      } catch (err: unknown) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleDelete(id: string) {
    if (!confirm("Delete this GPT?")) return;

    try {
      await deleteCustomGpt({ query: { gpt_id: id } });
      setGpts((prev) =>
        prev.filter((g) => g.customgptIdOrNullIfDefault !== id)
      );
    } catch (err: unknown) {
      alert(`Delete failed: ${(err as Error).message}`);
    }
  }

  if (loading) return <p className="center">Loading…</p>;
  if (error) return <p className="center">Error: {error}</p>;

  return (
    <div className="gpt-list-root">
      <h2 className="header">My GPTs</h2>

      {gpts.length === 0 && (
        <p className="center">You have no custom GPTs yet.</p>
      )}

      {gpts.map(({ customgptIdOrNullIfDefault, customGptName }) => (
        <div key={customgptIdOrNullIfDefault} className="gpt-row">
          <span className="gpt-name">{customGptName}</span>

          <div className="btn-group">
            <button
              type="button"
              onClick={() =>
                navigate("/chatWindow", {
                  state: {
                    gptIdOrNullIfDefault: customgptIdOrNullIfDefault,
                    chatId: null,
                  },
                })
              }
              className="btn primary"
            >
              Chat
            </button>
            <button
              type="button"
              onClick={() =>
                navigate(`/createOrEditCustomGPT/${customgptIdOrNullIfDefault}`)
              }
              className="btn secondary"
            >
              Edit
            </button>
            <button
              type="button"
              onClick={() => handleDelete(customgptIdOrNullIfDefault)}
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
