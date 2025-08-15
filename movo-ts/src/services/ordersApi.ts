import axios from "axios";
import { API_BASE } from "../config";

// استخدام API_BASE الموحد بدلًا من قراءة env محليًا
const API_URL: string = API_BASE;

// خريطة الحالات لتطابق قيم الـ backend
const STATUS_MAP: Record<string, string> = {
  "قيد الانتظار": "pending",
  "تعيين كابتن": "accepted", // كان: تم تعيين الكابتن
  "معالجة": "processing",
  "خرج للتوصيل": "out_for_delivery",
  "تم التوصيل": "delivered",
  "ملغي": "cancelled",
  "مؤجل": "waiting_restaurant_acceptance", // لا توجد حالة delayed في الـ backend الحالي
  "مشكلة": "processing", // لا توجد حالة issue فعلية
  "بانتظار قبول المطعم": "waiting_restaurant_acceptance",
  "جاهز للاستلام": "pick_up_ready",
};

const allowedStatuses: Set<string> = new Set([
  "pending",
  "accepted",
  "processing",
  "out_for_delivery",
  "delivered",
  "cancelled",
  "waiting_restaurant_acceptance",
  "pick_up_ready",
]);

function mapStatus(status?: string): string | undefined {
  if (!status) return undefined;
  const mapped = STATUS_MAP[status] ?? status;
  return allowedStatuses.has(mapped) ? mapped : undefined;
}

export async function getOrdersByStatus(status?: string) {
  const mapped = mapStatus(status);
  const params = mapped ? { order_status: mapped } : undefined;
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