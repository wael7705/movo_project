import axios from "axios";

const API_URL: string =
  (import.meta as any)?.env?.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// الخريطة بين النصوص العربية وحالات الطلب في الـ API
const STATUS_MAP: Record<string, string> = {
  "قيد الانتظار": "pending",
  "تم تعيين الكابتن": "captain_assigned",
  "معالجة": "processing",
  "خرج للتوصيل": "out_for_delivery",
  "تم التوصيل": "delivered",
  "ملغي": "cancelled",
  "مؤجل": "delayed",
  "مشكلة": "issue",
  "بانتظار قبول المطعم": "waiting_restaurant_acceptance",
  "جاهز للاستلام": "pick_up_ready",
};

const allowedStatuses: Set<string> = new Set(Object.values(STATUS_MAP));

function mapStatus(status?: string): string | undefined {
  if (!status) return undefined;
  const mapped = STATUS_MAP[status] ?? status;
  return allowedStatuses.has(mapped) ? mapped : undefined;
}

export async function getOrdersByStatus(status?: string) {
  const mapped = mapStatus(status);
  const params = mapped ? { status: mapped } : undefined;
  const res = await axios.get(`${API_URL}/orders`, { params });
  return res.data;
}

export async function getOrder(orderId: number | string) {
  const res = await axios.get(`${API_URL}/orders/${orderId}`);
  return res.data;
}

export async function updateOrderStatus(
  orderId: number | string,
  newStatus: string,
  captainId?: number
) {
  const mapped = mapStatus(newStatus) ?? newStatus;
  const res = await axios.put(`${API_URL}/orders/${orderId}`, {
    status: mapped,
    captain_id: captainId,
  });
  return res.data;
}