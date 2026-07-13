const BASE = "/api";

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${BASE}/health`);
  return handle(res);
}

export async function submitAlert(alert) {
  const res = await fetch(`${BASE}/alerts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(alert),
  });
  return handle(res);
}

export async function sendChatMessage(question, machineId) {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, machine_id: machineId || null }),
  });
  return handle(res);
}

export async function getInventory() {
  const res = await fetch(`${BASE}/inventory`);
  return handle(res);
}

export async function uploadManual(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE}/ingest`, { method: "POST", body: formData });
  return handle(res);
}
