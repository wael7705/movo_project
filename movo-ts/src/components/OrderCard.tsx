import React from 'react';

interface OrderCardProps {
  order_id: number;
  customer_name?: string;
  restaurant_name?: string;
  payment_method?: string;
  time_created?: string;
  status: string;
  vip?: boolean;
  first_order?: boolean;
  lang?: 'ar' | 'en';
}

const statusColors: Record<string, string> = {
  pending: 'text-yellow-600',
  processing: 'text-blue-600',
  delivered: 'text-green-600',
  cancelled: 'text-red-600',
  delayed: 'text-orange-600',
  issue: 'text-red-500',
  captain_assigned: 'text-purple-600',
  out_for_delivery: 'text-cyan-600',
};

const statusLabels: Record<string, { ar: string; en: string }> = {
  pending: { ar: 'قيد الانتظار', en: 'Pending' },
  processing: { ar: 'قيد المعالجة', en: 'Processing' },
  delivered: { ar: 'تم التوصيل', en: 'Delivered' },
  cancelled: { ar: 'ملغي', en: 'Cancelled' },
  delayed: { ar: 'مؤجل', en: 'Delayed' },
  issue: { ar: 'مشكلة', en: 'Issue' },
  captain_assigned: { ar: 'تم تعيين الكابتن', en: 'Captain Assigned' },
  out_for_delivery: { ar: 'خرج للتوصيل', en: 'Out for Delivery' },
};

const OrderCard: React.FC<OrderCardProps> = ({
  order_id,
  customer_name,
  restaurant_name,
  payment_method,
  time_created,
  status,
  vip,
  first_order,
  lang = 'ar',
}) => {
  return (
    <div
      className={`bg-white rounded-xl shadow-md border p-5 mb-4 flex flex-col gap-2 transition hover:shadow-lg relative ${vip ? 'border-pink-400' : 'border-gray-200'}`}
      style={{ minWidth: 260, maxWidth: 500 }}
      dir={lang === 'ar' ? 'rtl' : 'ltr'}
    >
      <div className="flex justify-between items-center mb-1">
        <span className="font-bold text-lg text-purple-800">#{order_id}</span>
        <span className={`font-semibold ${statusColors[status] || 'text-gray-500'}`}>{statusLabels[status]?.[lang] || status}</span>
      </div>
      <div className={lang === 'ar' ? 'text-right' : 'text-left'}>
        <div className="font-medium text-gray-800">{customer_name}</div>
        <div className="text-sm text-gray-500">{lang === 'ar' ? 'مطعم:' : 'Restaurant:'} {restaurant_name}</div>
        <div className="text-sm text-gray-500">{lang === 'ar' ? 'الدفع:' : 'Payment:'} {payment_method}</div>
        <div className="text-sm text-gray-400">{lang === 'ar' ? 'وقت الإنشاء:' : 'Created:'} {time_created}</div>
      </div>
      <div className="flex gap-2 mt-2 flex-wrap">
        {vip && <span className="bg-pink-100 text-pink-600 px-2 py-1 rounded-full text-xs font-bold">VIP</span>}
        {first_order && <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-bold">{lang === 'ar' ? 'أول طلب' : 'First Order'}</span>}
      </div>
      <div className={`flex gap-2 mt-3 flex-wrap ${lang === 'ar' ? 'justify-end' : 'justify-start'}`}> 
        <button className="px-3 py-1 rounded bg-yellow-400 text-white font-semibold hover:bg-yellow-500 transition">{lang === 'ar' ? 'توصيل' : 'Deliver'}</button>
        <button className="px-3 py-1 rounded bg-purple-100 text-purple-700 font-semibold hover:bg-purple-200 transition">{lang === 'ar' ? 'فاتورة' : 'Invoice'}</button>
        <button className="px-3 py-1 rounded bg-gray-100 text-gray-700 font-semibold hover:bg-gray-200 transition">{lang === 'ar' ? 'ملاحظات' : 'Notes'}</button>
        <button className="px-3 py-1 rounded bg-blue-100 text-blue-700 font-semibold hover:bg-blue-200 transition">{lang === 'ar' ? 'تعديل العنوان' : 'Edit Address'}</button>
      </div>
    </div>
  );
};

export default OrderCard; 