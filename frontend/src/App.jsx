import { useEffect, useState } from "react";
import StatusStrip from "./components/StatusStrip.jsx";
import AlertForm from "./components/AlertForm.jsx";
import DiagnosticOutput from "./components/DiagnosticOutput.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import InventoryPanel from "./components/InventoryPanel.jsx";
import { getHealth, submitAlert } from "./api.js";

const TABS = [
  { id: "console", label: "Alert Console" },
  { id: "chat", label: "Ask the Manuals" },
  { id: "inventory", label: "Inventory" },
];

export default function App() {
  const [tab, setTab] = useState("console");
  const [health, setHealth] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealth = () => getHealth().then(setHealth).catch(() => setHealth(null));
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleAlertSubmit = async (alert) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await submitAlert(alert);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="shell">
      <header className="header">
        <div className="brand">
          <span className="brand-mark">Prescriptive Maintenance Assistant</span>
          <span className="brand-sub">Agentic RAG · Industry 5.0</span>
        </div>
        <StatusStrip health={health} />
      </header>

      <nav className="tabbar">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === "console" && (
        <div className="grid">
          <div className="panel">
            <h2 className="panel-title">Simulated IoT Alert</h2>
            <p className="panel-desc">
              Enter or edit the incoming alert payload as if it arrived from the machine's
              controller.
            </p>
            <AlertForm onSubmit={handleAlertSubmit} loading={loading} />
          </div>
          <DiagnosticOutput result={result} loading={loading} error={error} />
        </div>
      )}

      {tab === "chat" && <ChatPanel />}
      {tab === "inventory" && <InventoryPanel />}
    </div>
  );
}
