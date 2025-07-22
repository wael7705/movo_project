import React from 'react';

interface Order {
  // Define order properties as needed
  [key: string]: any;
}

interface OrdersTableProps {
  status: string;
  orders: Order[];
}

const OrdersTable: React.FC<OrdersTableProps> = ({ status, orders }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full table-auto border text-sm">
        <thead className="bg-purple-100">
          <tr className="text-right text-purple-800">
            <th className="border px-3 py-2">#</th>
            <th className="border px-3 py-2">اسم الزبون</th>
            <th className="border px-3 py-2">المطعم</th>
            <th className="border px-3 py-2">طريقة الدفع</th>
            <th className="border px-3 py-2">وقت الإنشاء</th>
            <th className="border px-3 py-2">الحالة</th>
          </tr>
        </thead>
        <tbody>
          {orders.length === 0 ? (
            <tr className="text-center">
              <td colSpan={6} className="border px-3 py-4 text-gray-400">لا توجد طلبات حالياً</td>
            </tr>
          ) : (
            orders.map((order, idx) => (
              <tr key={order.id || idx} className="text-right">
                <td className="border px-3 py-2">{idx + 1}</td>
                <td className="border px-3 py-2">{order.customerName}</td>
                <td className="border px-3 py-2">{order.restaurantName}</td>
                <td className="border px-3 py-2">{order.paymentMethod}</td>
                <td className="border px-3 py-2">{order.createdAt}</td>
                <td className="border px-3 py-2 text-yellow-600 font-semibold">{order.status}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default OrdersTable;
