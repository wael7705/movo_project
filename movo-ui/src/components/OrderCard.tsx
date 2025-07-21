import React from 'react';

export interface Order {
  id: string;
  track_id: string;
  customer: string;
  customer_phone: string;
  restaurant: string;
  delivery: string;
  payment: string;
  ai_status: string;
  vip: boolean;
  first_order: boolean;
}

interface Props {
  order: Order;
  showDelivery?: boolean;
}

export const OrderCard: React.FC<Props> = ({ order, showDelivery }) => {
  const label = order.first_order ? "🟢 First Order" : "";
  const color = order.vip ? "#fff0f5" : "#f0f0f0";

  return (
    <div style={{ backgroundColor: color, color: "#222", padding: 16, borderRadius: 10, marginBottom: 16, border: "2px solid #d3d3d3" }}>
      <div><strong>Order ID:</strong> {order.id} &nbsp; | &nbsp; <strong>Track ID:</strong> {order.track_id}</div>
      <div><strong>Customer:</strong> {order.customer} | {order.customer_phone}</div>
      <div><strong>Restaurant:</strong> {order.restaurant}</div>
      <div><strong>Delivery:</strong> {order.delivery}</div>
      <div><strong>Payment:</strong> {order.payment}</div>
      <div><strong>AI Status:</strong> {order.ai_status}</div>
      <div>{order.vip ? "🌟 VIP" : ""} {label}</div>
      <div><strong>Timer:</strong> ⏱️ 00:00:00</div>
      <div style={{ marginTop: 10 }}>
        {showDelivery ? <button style={{ margin: 4 }}>Delivery</button> : <button style={{ margin: 4 }}>Invoice</button>}
        <button style={{ margin: 4 }}>📝 Notes</button>
        <button style={{ margin: 4 }}>📍 Edit Address</button>
      </div>
    </div>
  );
};