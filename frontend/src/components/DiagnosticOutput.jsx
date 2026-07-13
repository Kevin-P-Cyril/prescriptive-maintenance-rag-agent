import { useState } from "react";

function CitationChips({ citations }) {
  const [openIndex, setOpenIndex] = useState(null);

  if (!citations?.length) return null;

  return (
    <>
      <h3 className="section-title">Manual Citations</h3>
      <div className="citation-row">
        {citations.map((c, i) => (
          <button
            key={i}
            type="button"
            className="citation-chip"
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
          >
            {c.source} <span className="pg">p.{c.page}</span>
          </button>
        ))}
      </div>
      {openIndex !== null && citations[openIndex] && (
        <div className="citation-detail">"{citations[openIndex].snippet}…"</div>
      )}
    </>
  );
}

function PartsGrid({ parts }) {
  if (!parts?.length) return null;
  return (
    <>
      <h3 className="section-title">Spare Parts Check</h3>
      <div className="parts-grid" style={{ marginBottom: 22 }}>
        {parts.map((p, i) => (
          <div className="part-card" key={i}>
            <div className="part-name">{p.part_name}</div>
            <span className={`part-status ${p.in_stock ? "ok" : "out"}`}>
              <span className="dot" />
              {p.in_stock ? `In stock · ${p.quantity} units` : "Out of stock"}
            </span>
            {p.location && <div className="part-loc">{p.location}</div>}
          </div>
        ))}
      </div>
    </>
  );
}

export default function DiagnosticOutput({ result, loading, error }) {
  if (error) {
    return (
      <div className="panel">
        <div className="error-banner">ERROR: {error}</div>
        <p className="panel-desc">
          Make sure the backend is running and Ollama is reachable (see README for setup).
        </p>
      </div>
    );
  }

  if (!result && !loading) {
    return (
      <div className="panel">
        <div className="output-empty">
          <div className="glyph">◈</div>
          <div>Submit a machine alert to generate a cited repair procedure.</div>
        </div>
      </div>
    );
  }

  if (loading && !result) {
    return (
      <div className="panel">
        <div className="output-empty">
          <div className="glyph">⟳</div>
          <div>Retrieving manual sections and checking inventory…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="panel">
      <div className="diagnosis-block">
        <div className="diagnosis-eyebrow">
          Diagnosis · Machine {result.machine_id}
        </div>
        <div className="diagnosis-text">{result.diagnosis || "No diagnosis returned."}</div>
      </div>

      {result.steps?.length > 0 && (
        <>
          <h3 className="steps-title">Repair Procedure</h3>
          <ol className="step-list">
            {result.steps.map((step, i) => (
              <li className="step-item" key={i}>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </>
      )}

      <CitationChips citations={result.citations} />
      <PartsGrid parts={result.parts_required} />
    </div>
  );
}
