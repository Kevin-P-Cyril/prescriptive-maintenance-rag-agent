import { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../api.js";

export default function ChatPanel() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await sendChatMessage(question);
      const citationText = res.citations?.length
        ? "\n\nSources: " + res.citations.map((c) => `${c.source} p.${c.page}`).join(", ")
        : "";
      setMessages((prev) => [...prev, { role: "assistant", text: res.answer + citationText }]);
    } catch (err) {
      setError(err.message);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Sorry — I couldn't process that: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2 className="panel-title">Ask the Manuals</h2>
      <p className="panel-desc">
        Ask any free-form maintenance question. The agent retrieves relevant manual sections
        and cites the exact page for every claim.
      </p>

      <div className="chat-log" ref={logRef}>
        {messages.length === 0 && (
          <div className="output-empty" style={{ padding: "30px 10px", minHeight: "auto" }}>
            Try: "How do I fix drive belt slippage on the CNC-204?"
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role}`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="chat-msg assistant">Thinking…</div>}
      </div>

      {error && <div className="error-banner">ERROR: {error}</div>}

      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a maintenance question…"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
