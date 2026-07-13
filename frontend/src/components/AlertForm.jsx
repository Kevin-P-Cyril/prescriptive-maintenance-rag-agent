import { useState } from "react";

const SEVERITIES = ["low", "medium", "high", "critical"];

const DEFAULT_ALERT = {
  machine_id: "CNC-204",
  machine_type: "CNC Milling Machine",
  error_code: "E-108",
  description: "Spindle overheating detected during operation",
  severity: "high",
  sensor_reading: "Spindle temp: 92°C (threshold: 75°C)",
};

export default function AlertForm({ onSubmit, loading }) {
  const [alert, setAlert] = useState(DEFAULT_ALERT);

  const update = (field) => (e) => setAlert({ ...alert, [field]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(alert);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="machine_id">Machine ID</label>
        <input id="machine_id" value={alert.machine_id} onChange={update("machine_id")} required />
      </div>

      <div className="field">
        <label htmlFor="machine_type">Machine Type</label>
        <input id="machine_type" value={alert.machine_type} onChange={update("machine_type")} required />
      </div>

      <div className="field">
        <label htmlFor="error_code">Error Code</label>
        <input id="error_code" value={alert.error_code} onChange={update("error_code")} required />
      </div>

      <div className="field">
        <label htmlFor="description">Alert Description</label>
        <textarea id="description" value={alert.description} onChange={update("description")} required />
      </div>

      <div className="field">
        <label htmlFor="sensor_reading">Sensor Reading (optional)</label>
        <input id="sensor_reading" value={alert.sensor_reading} onChange={update("sensor_reading")} />
      </div>

      <div className="field">
        <label>Severity</label>
        <div className="severity-row">
          {SEVERITIES.map((level) => (
            <button
              type="button"
              key={level}
              data-level={level}
              className={`severity-btn ${alert.severity === level ? "active" : ""}`}
              onClick={() => setAlert({ ...alert, severity: level })}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      <button className="btn-primary" type="submit" disabled={loading}>
        {loading ? (
          <>
            <span className="spinner" />
            Diagnosing…
          </>
        ) : (
          "Run Diagnostic Agent"
        )}
      </button>

      <p className="hint">
        This simulates an IoT alert arriving from the machine's controller. The agent will
        retrieve relevant manual sections, check spare-parts inventory, and generate cited
        repair steps.
      </p>
    </form>
  );
}
