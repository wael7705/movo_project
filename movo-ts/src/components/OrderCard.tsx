import React from 'react';
import UseSafeButton from './UseSafeButton';

// Icons (using simple text-based icons for now)
const Icons = {
  arrowRight: '→',
  cancel: '✕',
  receipt: '📄',
  note: '📝',
  bug: '🐛',
  check: '✓',
  location: '📍',
  star: '⭐',
};

interface OrderCardProps {
  order_id: number;
  customer_name?: string;
  restaurant_name?: string;
  payment_method?: string;
  created_at?: string;
  status: string;
  vip?: boolean;
  first_order?: boolean;
  lang?: 'ar' | 'en';
  onStatusChange?: (orderId: number, newStatus: string) => void;
  onInvoice?: (orderId: number) => void;
  onNotes?: (orderId: number) => void;
  onTrack?: (orderId: number) => void;
  // onRate?: (orderId: number) => void; // تم إلغاء زر التقييم
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
  created_at,
  status,
  vip,
  first_order,
  lang = 'ar',
  onStatusChange,
  onInvoice,
  onNotes,
  onTrack,
  // onRate,
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
        <div className="text-sm text-gray-400">{lang === 'ar' ? 'وقت الإنشاء:' : 'Created:'} {created_at}</div>
      </div>
      <div className="flex gap-2 mt-2 flex-wrap">
        {vip && <span className="bg-pink-100 text-pink-600 px-2 py-1 rounded-full text-xs font-bold">VIP</span>}
        {first_order && <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-bold">{lang === 'ar' ? 'أول طلب' : 'First Order'}</span>}
      </div>
      <div className={`flex gap-2 mt-3 flex-wrap ${lang === 'ar' ? 'justify-end' : 'justify-start'}`}> 
        {/* Status-specific buttons */}
        {status === 'pending' && (
          <>
            <UseSafeButton onAction={() => onStatusChange?.(order_id, 'choose_captain')}>
              <span className="px-3 py-1 rounded bg-green-600 text-white font-semibold hover:bg-green-700 transition inline-flex items-center gap-1">
                <span>{Icons.arrowRight}</span>
                {lang === 'ar' ? 'التالي' : 'Next'}
              </span>
            </UseSafeButton>
            <UseSafeButton onAction={() => onStatusChange?.(order_id, 'cancelled')}>
              <span className="px-3 py-1 rounded bg-red-100 text-red-700 font-semibold hover:bg-red-200 transition inline-flex items-center gap-1">
                <span>{Icons.cancel}</span>
                {lang === 'ar' ? 'إلغاء' : 'Cancel'}
              </span>
            </UseSafeButton>
          </>
        )}

        {status === 'choose_captain' && (
          <>
            <UseSafeButton onAction={() => onStatusChange?.(order_id, 'processing')}>
              <span className="px-3 py-1 rounded bg-green-600 text-white font-semibold hover:bg-green-700 transition inline-flex items-center gap-1">
                <span>{Icons.check}</span>
                {lang === 'ar' ? 'تعيين' : 'Assign'}
              </span>
            </UseSafeButton>
            <UseSafeButton onAction={() => onStatusChange?.(order_id, 'cancelled')}>
              <span className="px-3 py-1 rounded bg-red-100 text-red-700 font-semibold hover:bg-red-200 transition inline-flex items-center gap-1">
                <span>{Icons.cancel}</span>
                {lang === 'ar' ? 'إلغاء' : 'Cancel'}
              </span>
            </UseSafeButton>
          </>
        )}

        {(status === 'processing' || status === 'waiting_approval' || status === 'preparing') && (
          <>
            <UseSafeButton onAction={() => {
              if (status === 'waiting_approval') {
                onStatusChange?.(order_id, 'preparing');
              } else if (status === 'preparing') {
                onStatusChange?.(order_id, 'captain_received');
              }
            }}>
              <span className="px-3 py-1 rounded bg-green-600 text-white font-semibold hover:bg-green-700 transition inline-flex items-center gap-1">
                <span>{Icons.arrowRight}</span>
                {lang === 'ar' ? 'التالي' : 'Next'}
              </span>
            </UseSafeButton>
            <UseSafeButton onAction={() => onStatusChange?.(order_id, 'cancelled')}>
              <span className="px-3 py-1 rounded bg-red-100 text-red-700 font-semibold hover:bg-red-200 transition inline-flex items-center gap-1">
                <span>{Icons.cancel}</span>
                {lang === 'ar' ? 'إلغاء' : 'Cancel'}
              </span>
            </UseSafeButton>
          </>
        )}

        {status === 'out_for_delivery' && (
          <>
            <button 
              className="px-3 py-1 rounded bg-blue-600 text-white font-semibold hover:bg-blue-700 transition flex items-center gap-1"
              onClick={() => onTrack?.(order_id)}
            >
              <span>{Icons.location}</span>
              {lang === 'ar' ? 'تتبع' : 'Track'}
            </button>
            <UseSafeButton onAction={() => onStatusChange?.(order_id, 'delivered')}>
              <span className="px-3 py-1 rounded bg-green-600 text-white font-semibold hover:bg-green-700 transition inline-flex items-center gap-1">
                <span>{Icons.arrowRight}</span>
                {lang === 'ar' ? 'التالي' : 'Next'}
              </span>
            </UseSafeButton>
          </>
        )}

        {/* تمت إزالة زر التقييم بطلبك */}

        {/* أزرار عامة لكل الحالات */}
        <button 
          className="px-3 py-1 rounded bg-purple-100 text-purple-700 font-semibold hover:bg-purple-200 transition flex items-center gap-1"
          onClick={() => onInvoice?.(order_id)}
        >
          <span>{Icons.receipt}</span>
          {lang === 'ar' ? 'فاتورة' : 'Invoice'}
        </button>
        
        <button 
          className="px-3 py-1 rounded bg-gray-100 text-gray-700 font-semibold hover:bg-gray-200 transition flex items-center gap-1"
          onClick={() => onNotes?.(order_id)}
        >
          <span>{Icons.note}</span>
          {lang === 'ar' ? 'ملاحظات' : 'Notes'}
        </button>

        {/* زر اختيار كابتن ينقل الطلب إلى تبويب اختيار كابتن */}
        <UseSafeButton onAction={() => onStatusChange?.(order_id, 'captain_assigned')}>
          <span className="px-3 py-1 rounded bg-purple-600 text-white font-semibold hover:bg-purple-700 transition inline-flex items-center gap-1">
            <span>{Icons.check}</span>
            {lang === 'ar' ? 'اختيار كابتن' : 'Select Captain'}
          </span>
        </UseSafeButton>

        {/* زر إلغاء عام */}
        <UseSafeButton onAction={() => onStatusChange?.(order_id, 'cancelled')}>
          <span className="px-3 py-1 rounded bg-red-600 text-white font-semibold hover:bg-red-700 transition inline-flex items-center gap-1">
            <span>{Icons.cancel}</span>
            {lang === 'ar' ? 'إلغاء' : 'Cancel'}
          </span>
        </UseSafeButton>

        {/* زر مشكلة (اختياري) لكل الحالات عدا تم التوصيل/ملغي */}
        {!['delivered', 'cancelled'].includes(status) && (
          <UseSafeButton onAction={() => onStatusChange?.(order_id, 'problem')}>
            <span className="px-3 py-1 rounded bg-orange-100 text-orange-700 font-semibold hover:bg-orange-200 transition inline-flex items-center gap-1">
              <span>{Icons.bug}</span>
              {lang === 'ar' ? 'مشكلة' : 'Problem'}
            </span>
          </UseSafeButton>
        )}
      </div>
    </div>
  );
};

export default OrderCard; 