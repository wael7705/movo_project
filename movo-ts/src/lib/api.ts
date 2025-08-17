import { QueryClient } from "@tanstack/react-query";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
export const queryClient = new QueryClient();

async function toJson(response: Response) {
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  health: () => fetch(`${BASE}/db_ping`).then(toJson),
  // ملاحظة: الواجهة الأمامية تعتمد الآن على /orders الموحّد وإرجاع current_status
  orders: {
    list: (params?: Record<string, string | number | boolean>) => {
      const qs = params
        ? `?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`
        : '';
      return fetch(`${BASE}/orders${qs}`).then(toJson);
    },
    byId: (id: number | string) => fetch(`${BASE}/orders/${id}`).then(toJson),
    updateStatus: async (id: number | string, status: string) => {
      // تطبيع الحالة لتتوافق مع enum الموجود في قاعدة البيانات
      const map: Record<string, string> = {
        captain_assigned: 'accepted',
        choose_captain: 'accepted',
        waiting_approval: 'processing',
        preparing: 'processing',
        captain_received: 'processing',
        problem: 'processing',
        delayed: 'processing',
        issue: 'processing',
      };
      const normalized = map[status] ?? status;
      const res = await fetch(`${BASE}/orders/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: normalized }),
      }).then(toJson);
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
    },
    counts: () => fetch(`${BASE}/orders/counts`).then(toJson),
  },
};

export default api;


