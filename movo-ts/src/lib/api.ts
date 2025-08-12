const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

async function toJson(response: Response) {
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  health: () => fetch(`${BASE}/db_ping`).then(toJson),
  orders: {
    list: (params?: Record<string, string | number | boolean>) => {
      const qs = params
        ? `?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`
        : '';
      return fetch(`${BASE}/orders${qs}`).then(toJson);
    },
    byId: (id: number | string) => fetch(`${BASE}/orders/${id}`).then(toJson),
    notes: {
      listByOrder: (id: number | string) => fetch(`${BASE}/orders/${id}/notes`).then(toJson),
    },
  },
};

export default api;


