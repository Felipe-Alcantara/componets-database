/** Cliente da API do Felixo UI Index. Usa /api (proxy do Vite em dev). */

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Erro ${res.status}`);
  }
  return res.json();
}

export function fetchFilters() {
  return getJSON("/api/filters");
}

export function fetchComponents(params) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== "" && v !== null && v !== undefined && v !== false) qs.set(k, v);
  });
  return getJSON(`/api/components?${qs.toString()}`);
}

export function fetchComponent(externalId) {
  return getJSON(`/api/components/${encodeURIComponent(externalId)}`);
}
