import { Order } from "@/components/OrderCard";

export const mockOrders: Order[] = [
    {
        id: "ORD-001",
        track_id: "TRK-123",
        customer: "وائل الزعيم",
        customer_phone: "+963-999999999",
        restaurant: "شاورما الأبطال",
        delivery: "كابتن سامر",
        payment: "كاش",
        ai_status: "معالجة تلقائية - بدون مشاكل",
        vip: true,
        first_order: true,
    },
    {
        id: "ORD-002",
        track_id: "TRK-456",
        customer: "علي الحمصي",
        customer_phone: "+963-988888888",
        restaurant: "بيتزا زينو",
        delivery: "كابتن هادي",
        payment: "أونلاين",
        ai_status: "مشكلة بالعنوان",
        vip: false,
        first_order: false,
    }
];