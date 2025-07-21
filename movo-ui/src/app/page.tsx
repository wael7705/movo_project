import { OrderCard } from "@/components/OrderCard";
import { mockOrders } from "@/lib/data";

export default function Home() {
  return (
    <main className="p-8 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">طلبات اليوم</h1>
      <div className="space-y-4">
        {mockOrders.map((order) => (
          <OrderCard key={order.id} order={order} showDelivery />
        ))}
      </div>
    </main>
  );
}