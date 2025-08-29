import axios from "axios";
import { API_BASE } from "../config";
import { makeAbortable } from "../api/http";

// استخدام API_BASE الموحد بدلًا من قراءة env محليًا
const API_URL: string = API_BASE;

// خريطة الحالات لتطابق قيم الـ backend
const STATUS_MAP: Record<string, string> = {
  "قيد الانتظار": "pending",
  "تعيين كابتن": "choose_captain",
  "معالجة": "processing",
  "خرج للتوصيل": "out_for_delivery",
  "تم التوصيل": "delivered",
  "ملغي": "cancelled",
  "مشكلة": "problem",
  "بانتظار قبول المطعم": "choose_captain",
  "جاهز للاستلام": "processing",
};

const allowedStatuses: Set<string> = new Set([
  "pending",
  "choose_captain",
  "processing",
  "out_for_delivery",
  "delivered",
  "cancelled",
  "problem",
  "deferred",
  "pickup",
]);

function mapStatus(status?: string): string | undefined {
  if (!status) return undefined;
  const mapped = STATUS_MAP[status] ?? status;
  return allowedStatuses.has(mapped) ? mapped : undefined;
}

const _getOrdersByStatus = async (status?: string, signal?: AbortSignal) => {
  const mapped = mapStatus(status);
  const params = mapped ? { order_status: mapped } : undefined;
  const res = await axios.get(`${API_URL}/orders`, { params, signal });
  return res.data;
};
export const getOrdersByStatus = makeAbortable(_getOrdersByStatus);

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