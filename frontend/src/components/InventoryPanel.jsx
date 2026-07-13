import { useEffect, useState } from "react";
import { getInventory } from "../api.js";

export default function InventoryPanel() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getInventory()
      .then(setItems)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="panel">
      <h2 className="panel-title">Spare-Parts Inventory</h2>
      <p className="panel-desc">
        Mock warehouse inventory used by the agent's tool-call step to check part availability.
      </p>

      {loading && <div className="hint">Loading inventory…</div>}
      {error && <div className="error-banner">ERROR: {error}</div>}

      {!loading && !error && (
        <table className="inv-table">
          <thead>
            <tr>
              <th>Part</th>
              <th>SKU</th>
              <th>Qty</th>
              <th>Location</th>
              <th>Compatible Machines</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.sku}>
                <td className="name">{item.part_name}</td>
                <td>{item.sku}</td>
                <td>
                  <span className={`qty-pill ${item.quantity > 0 ? "ok" : "out"}`}>
                    {item.quantity > 0 ? item.quantity : "OUT"}
                  </span>
                </td>
                <td>{item.location}</td>
                <td>{item.compatible_machines.join(", ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
