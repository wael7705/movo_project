import React, { useEffect, useState } from 'react';

interface Order {
    // Define order properties as needed
    [key: string]: any;
    createdAt?: string;
    deliveredAt?: string;
    estimatedDeliveryTime?: string;
    status?: string;
}

interface OrdersTableProps {
    status: string;
    orders: Order[];
}

const getStageColor = (status: string, isLate: boolean) => {
    if (status === 'delivered') return 'text-green-600';
    if (isLate) return 'text-red-600';
    if (status === 'preparing' || status === 'pending') return 'text-yellow-600';
    return 'text-purple-800';
};

const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
};

const OrdersTable: React.FC<OrdersTableProps> = ({ orders }) => {
    // لكل طلب، عداد منفصل
    const [timers, setTimers] = useState<{[key: number]: number}>({});

    useEffect(() => {
        const interval = setInterval(() => {
            setTimers(() => {
                const updated: {[key: number]: number} = {};
                orders.forEach((order, idx) => {
                    const created = order.createdAt ? new Date(order.createdAt) : null;
                    const delivered = order.deliveredAt ? new Date(order.deliveredAt) : null;
                    const now = new Date();
                    if (created && !delivered) {
                        updated[idx] = Math.floor((now.getTime() - created.getTime()) / 1000);
                    } else if (created && delivered) {
                        updated[idx] = Math.floor((delivered.getTime() - created.getTime()) / 1000);
                    } else {
                        updated[idx] = 0;
                    }
                });
                return updated;
            });
        }, 1000);
        return () => clearInterval(interval);
    }, [orders]);

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
                        <th className="border px-3 py-2">عداد الوقت</th>
                    </tr>
                </thead>
                <tbody>
                    {orders.length === 0 ? (
                        <tr className="text-center">
                            <td colSpan={7} className="border px-3 py-4 text-gray-400">لا توجد طلبات حالياً</td>
                        </tr>
                    ) : (
                        orders.map((order, idx) => {
                            const timer = timers[idx] || 0;
                            // إذا كان هناك estimatedDeliveryTime، احسب الوقت المتبقي
                            let remaining = null;
                            let isLate = false;
                            if (order.estimatedDeliveryTime && order.status !== 'delivered') {
                                const est = new Date(order.estimatedDeliveryTime);
                                const now = new Date();
                                const diff = Math.floor((est.getTime() - now.getTime()) / 1000);
                                remaining = diff;
                                if (diff < 0) isLate = true;
                            }
                            return (
                                <tr key={order.id || idx} className="text-right">
                                    <td className="border px-3 py-2">{idx + 1}</td>
                                    <td className="border px-3 py-2">{order.customerName}</td>
                                    <td className="border px-3 py-2">{order.restaurantName}</td>
                                    <td className="border px-3 py-2">{order.paymentMethod}</td>
                                    <td className="border px-3 py-2">{order.createdAt}</td>
                                    <td className="border px-3 py-2 text-yellow-600 font-semibold">{order.status}</td>
                                    <td className={`border px-3 py-2 font-bold ${getStageColor(order.status ?? '', isLate)}`}>{
                                        order.status === 'delivered'
                                            ? formatDuration(timer)
                                            : remaining !== null
                                                ? (isLate ? 'متأخر ' : 'متبقي ') + formatDuration(Math.abs(remaining))
                                                : formatDuration(timer)
                                    }</td>
                                </tr>
                            );
                        })
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default OrdersTable;
