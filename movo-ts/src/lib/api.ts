import { QueryClient } from "@tanstack/react-query";
import { makeAbortable } from "../api/http";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
export const queryClient = new QueryClient();

async function toJson(response: Response) {
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function _fetchJSON(url: string, signal?: AbortSignal) {
  const res = await fetch(url, { signal, headers: { Accept: "application/json" } });
  return toJson(res);
}

export const fetchCounts = makeAbortable((signal?: AbortSignal) => _fetchJSON(`${BASE}/orders/counts`, signal));

const listAbortable = makeAbortable((params?: Record<string, string | number | boolean>, signal?: AbortSignal) => {
  const qs = params ? `?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}` : '';
  return _fetchJSON(`${BASE}/orders${qs}`, signal);
});

export const api = {
  health: () => fetch(`${BASE}/db_ping`).then(toJson),
  orders: {
    list: (params?: Record<string, string | number | boolean>) => listAbortable(params),
    byId: (id: number | string) => fetch(`${BASE}/orders/${id}`).then(toJson),
    updateStatus: async (id: number | string, status: string) => {
      const map: Record<string, string> = {
        captain_assigned: 'choose_captain',
        choose_captain: 'choose_captain',
        waiting_approval: 'processing',
        preparing: 'processing',
        captain_received: 'processing',
        problem: 'problem',
        delayed: 'deferred',
        issue: 'problem',
        deferred: 'deferred',
        pickup: 'pickup',
      };
      const normalized = map[status] ?? status;
      // استخدم مسارات محددة للحالات الخاصة
      let res;
      if (normalized === 'problem') {
        res = await fetch(`${BASE}/orders/${id}/problem`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
        }).then(toJson);
      } else {
        res = await fetch(`${BASE}/orders/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: normalized }),
        }).then(toJson);
      }
      await queryClient.invalidateQueries({ queryKey: ["orders"] });
      return res;
    },
    createDemo: async () => {
      const res = await fetch(`${BASE}/orders/demo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }).then(toJson);
      await queryClient.invalidateQueries({ queryKey: ["orders"] });
      return res;
    },
    next: async (id: number | string) => {
      const res = await fetch(`${BASE}/orders/${id}/next`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
      }).then(toJson);
      await queryClient.invalidateQueries({ queryKey: ["orders"] });
      return res;
    },
    cancel: async (id: number | string) => {
      const res = await fetch(`${BASE}/orders/${id}/cancel`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
      }).then(toJson);
      await queryClient.invalidateQueries({ queryKey: ["orders"] });
      return res;
    },
    notes: {
      listByOrder: (id: number | string) => fetch(`${BASE}/orders/${id}/notes`).then(toJson),
      add: (id: number | string, note_text: string, source: 'employee'|'ai'='employee') =>
        fetch(`${BASE}/orders/${id}/notes`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ note_text, source }),
        }).then(toJson),
    },
    insights: {
      order: (id: number | string) => fetch(`${BASE.replace('/api/v1','')}/api/v1/analytics/insights/order/${id}`).then(toJson),
    },
    counts: () => fetch(`${BASE}/orders/counts`).then(toJson),
  },
};

export default api;


