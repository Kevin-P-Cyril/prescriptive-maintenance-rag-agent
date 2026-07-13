export default function StatusStrip({ health }) {
  const ollamaOn = health?.ollama_reachable;
  const chunks = health?.indexed_chunks ?? "—";

  return (
    <div className="status-strip">
      <span>
        <span className={`status-dot ${ollamaOn ? "on" : "off"}`} />
        LLM {ollamaOn ? "ONLINE" : "OFFLINE"}
      </span>
      <span>MANUAL INDEX: {chunks} CHUNKS</span>
    </div>
  );
}
