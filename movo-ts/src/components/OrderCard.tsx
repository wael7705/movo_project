import React from 'react';

type CustomerTier = 'regular' | 'vip' | 'movo_plus';

interface OrderCardProps {
  order_id: number;
  customer_name?: string;
  customerName?: string;
  customer_phone?: string;
  customerPhone?: string;
  restaurant_name?: string;
  restaurantName?: string;
  restaurantAddress?: string;
  area?: string;
  payment_method?: string;
  paymentType?: string;
  status: string;
  current_status?: string;
  substage?: string;
  vip?: boolean;
  lang?: 'ar' | 'en';
  onStatusChange?: (orderId: number, newStatus: string) => void;
  onInvoice?: (orderId: number) => void;
  // New optional UI-only props (no logic changes)
  customerTier?: CustomerTier; // 'vip' | 'movo_plus' | 'regular'
  onInvoiceClick?: () => Promise<void> | void; // optional, mirrors existing invoice logic
  // Additional optional fields for display-only UI
  deliveryType?: string; // 'pickup' | 'movo' | etc
  delivery_method?: string; // backend enum mapping
  totalAmount?: number;
  total_price_customer?: number | string;
  cancelCountForCustomer?: number;
  totalDeliveryDurationSec?: number;
  orderId?: number;
  current_tab?: string;
  awaitingCaptain?: boolean;
  onAssignCaptainClick?: (orderId: number) => void;
}

const statusColors: Record<string, string> = {
  pending: 'text-yellow-600',
  choose_captain: 'text-purple-600',
  processing: 'text-blue-600',
  delivered: 'text-green-600',
  cancelled: 'text-red-600',
  problem: 'text-red-500',
  out_for_delivery: 'text-cyan-600',
  deferred: 'text-orange-600',
  pickup: 'text-purple-600',
};

const statusLabels: Record<string, { ar: string; en: string }> = {
  pending: { ar: 'قيد الانتظار', en: 'Pending' },
  choose_captain: { ar: 'تعيين كابتن', en: 'Captain Selection' },
  processing: { ar: 'قيد المعالجة', en: 'Processing' },
  delivered: { ar: 'تم التوصيل', en: 'Delivered' },
  cancelled: { ar: 'ملغي', en: 'Cancelled' },
  problem: { ar: 'مشكلة', en: 'Problem' },
  out_for_delivery: { ar: 'خرج للتوصيل', en: 'Out for Delivery' },
  deferred: { ar: 'مؤجل', en: 'Deferred' },
  pickup: { ar: 'استلام شخصي', en: 'Pickup' },
};

const substageLabels: Record<string, { ar: string; en: string }> = {
  waiting_approval: { ar: 'انتظار الموافقة', en: 'Waiting Approval' },
  preparing: { ar: 'التحضير', en: 'Preparing' },
  captain_received: { ar: 'الكابتن استلم', en: 'Captain Received' },
};

function GoldBadge({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold bg-gradient-to-r from-yellow-400 via-amber-300 to-yellow-500 text-yellow-900 border-yellow-600/40 shadow-[0_0_10px_rgba(250,204,21,0.35)]"
      title="Customer Status"
    >
      ✨ {children}
    </span>
  );
}

// صف معلومات بسيط
function InfoRow({ label, value }: { label: string; value?: React.ReactNode }) {
  if (value === undefined || value === null || value === "") return null;
  return (
    <div className="flex items-start gap-2 text-sm">
      <span className="min-w-28 text-slate-500">{label}:</span>
      <span className="text-slate-800 font-medium">{value}</span>
    </div>
  );
}

// تلميح زجاجي للعنوان عند تمرير الماوس
function HoverHint({ hint, children }: { hint?: string; children: React.ReactNode }) {
  return (
    <div className="group relative inline-flex items-center">
      {children}
      {hint && (
        <div className="pointer-events-none absolute z-20 hidden group-hover:block left-0 mt-2 w-[24rem] rounded-xl border border-slate-200 bg-white/85 backdrop-blur-sm shadow-lg p-3">
          <div className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">العنوان التفصيلي</div>
          <div className="text-sm text-slate-700 leading-5">{hint}</div>
        </div>
      )}
    </div>
  );
}

function formatHMS(totalSeconds: number): string {
  const sec = Math.max(0, Math.floor(totalSeconds));
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  const hh = h > 0 ? `${String(h).padStart(2, '0')}:` : '';
  return `${hh}${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

const OrderCard: React.FC<OrderCardProps> = ({
  order_id,
  customer_name,
  customerName,
  customer_phone,
  customerPhone,
  restaurant_name,
  restaurantName,
  restaurantAddress,
  area,
  payment_method,
  paymentType,
  status,
  current_status,
  substage,
  vip,
  lang = 'ar',
  onStatusChange,
  onInvoice,
  customerTier,
  onInvoiceClick,
  deliveryType,
  delivery_method,
  totalAmount,
  total_price_customer,
  cancelCountForCustomer,
  totalDeliveryDurationSec,
  orderId,
  current_tab,
  awaitingCaptain,
  onAssignCaptainClick,
}) => {
  // استخدام current_status إذا كان متوفراً، وإلا status
  const displayStatus = current_status || status;
  const name = customer_name ?? customerName;
  const phone = customer_phone ?? customerPhone;
  const rName = restaurant_name ?? restaurantName;
  const payType = paymentType ?? payment_method;
  const dType = (deliveryType ?? (delivery_method === 'pick_up' ? 'pickup' : delivery_method ? 'movo' : undefined)) as string | undefined;
  const totalAmountValue = totalAmount ?? (typeof total_price_customer === 'string' ? parseFloat(total_price_customer) : total_price_customer);
  const amountIsHigh = (totalAmountValue ?? 0) > 300000;
  const totalDeliverySecComputed = totalDeliveryDurationSec;
  
  return (
    <div
      className={`bg-white rounded-xl shadow-md border p-5 mb-4 flex flex-col gap-2 transition hover:shadow-lg relative ${vip ? 'border-pink-400' : 'border-gray-200'}`}
      style={{ minWidth: 260, maxWidth: 500 }}
      dir={lang === 'ar' ? 'rtl' : 'ltr'}
    >
      <div className="flex justify-between items-center mb-1">
        <span className="font-bold text-lg text-purple-800">#{order_id}</span>
        <div className="text-right">
          <div className={`font-semibold ${statusColors[displayStatus] || 'text-gray-500'}`}>
            {statusLabels[displayStatus]?.[lang] || displayStatus}
          </div>
          {awaitingCaptain && (
            <div className="text-xs text-amber-600 font-semibold">بانتظار قبول الكابتن… ⏳</div>
          )}
          {substage && displayStatus === 'processing' && (
            <div className="text-sm text-blue-600 font-medium">
              {substageLabels[substage]?.[lang] || substage}
            </div>
          )}
        </div>
      </div>
      {/* جسم البطاقة */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 px-5 py-4">
        {/* العمود الأيسر: المطعم + الموقع + التوصيل + الدفع */}
        <div className="space-y-2">
          <InfoRow
            label="المطعم"
            value={
              <HoverHint hint={restaurantAddress}>
                <span className="font-semibold">{rName}</span>
                {restaurantAddress && (
                  <span className="ml-2 text-xs text-slate-400">(مرّر للاطلاع على العنوان)</span>
                )}
              </HoverHint>
            }
          />
          <InfoRow label="المنطقة" value={area} />
          <InfoRow
            label="طريقة التوصيل"
            value={
              dType === 'pickup' ? (
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-500 text-white">Pickup</span>
              ) : dType ? (
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-600/10 text-emerald-700 border border-emerald-600/30">Movo Delivery</span>
              ) : undefined
            }
          />
          <InfoRow label="طريقة الدفع" value={payType} />
          <InfoRow
            label="الإجمالي"
            value={
              totalAmountValue !== undefined && !Number.isNaN(totalAmountValue) ? (
                <span className={amountIsHigh ? 'text-red-600 font-bold' : 'text-slate-900 font-bold'}>
                  {Number(totalAmountValue).toLocaleString()} <span className="text-sm font-medium text-slate-500">SYP</span>
                  {amountIsHigh && <span className="ml-2 text-xs text-red-600/80">(مبلغ مرتفع)</span>}
                </span>
              ) : undefined
            }
          />
        </div>

        {/* العمود الأيمن: العميل + ID + الإلغاءات + زمن التوصيل الكلي */}
        <div className="space-y-2">
          <InfoRow
            label="العميل"
            value={
              <span className="inline-flex items-center gap-2">
                <span className="font-semibold">{name}</span>
                {customerTier === 'vip' && <GoldBadge>VIP</GoldBadge>}
                {customerTier === 'movo_plus' && <GoldBadge>Movo&nbsp;Plus</GoldBadge>}
              </span>
            }
          />
          <InfoRow label="رقم العميل" value={phone} />
          <InfoRow label="ID الطلب" value={<span className="font-mono">#{order_id ?? orderId}</span>} />
          <InfoRow label="Cancel Orders" value={cancelCountForCustomer !== undefined ? <span className="font-semibold">{cancelCountForCustomer}</span> : undefined} />
          {totalDeliverySecComputed !== undefined && (
            <InfoRow label="مدة التوصيل" value={<span className="tabular-nums">{formatHMS(totalDeliverySecComputed)}</span>} />
          )}
        </div>
      </div>
      {/* شريط الأزرار السفلي — لا تغيير بالمنطق */}
      <div className="flex items-center justify-end gap-2 px-5 py-3 border-t bg-slate-50">
        {current_tab === 'choose_captain' && (
          <button
            onClick={() => onAssignCaptainClick?.(order_id)}
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 text-white text-sm px-3 py-2 hover:bg-emerald-700 transition"
            title={lang === 'ar' ? 'اختيار كابتن' : 'Assign Captain'}
          >
            🎯 <span className="sr-only">Assign</span>
          </button>
        )}
        {/* زر الانتقال/التالي */}
        <button
          onClick={() => onStatusChange?.(order_id, 'next')}
          disabled={!onStatusChange}
          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 text-white text-sm px-3 py-2 disabled:opacity-50 hover:bg-blue-700 transition"
          title={lang === 'ar' ? 'التالي / نقل التبويب' : 'Next / Advance'}
        >
          ➡️ <span className="sr-only">{lang === 'ar' ? 'التالي' : 'Next'}</span>
        </button>

        {/* زر الإلغاء */}
        <button
          onClick={() => onStatusChange?.(order_id, 'cancelled')}
          disabled={!onStatusChange}
          className="inline-flex items-center gap-2 rounded-xl bg-rose-600 text-white text-sm px-3 py-2 disabled:opacity-50 hover:bg-rose-700 transition"
          title={lang === 'ar' ? 'إلغاء الطلب' : 'Cancel Order'}
        >
          ❌ <span className="sr-only">{lang === 'ar' ? 'إلغاء' : 'Cancel'}</span>
        </button>

        {/* زر الفاتورة */}
        <button
          onClick={() => (onInvoiceClick ? onInvoiceClick() : onInvoice?.(order_id))}
          disabled={!(onInvoiceClick || onInvoice)}
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 text-white text-sm px-3 py-2 disabled:opacity-50 hover:bg-emerald-700 transition"
          title={lang === 'ar' ? 'عرض الفاتورة' : 'View Invoice'}
        >
          🧾 <span className="sr-only">{lang === 'ar' ? 'الفاتورة' : 'Invoice'}</span>
        </button>
      </div>

      {/* // REMOVED OLD BUTTONS (icons...) — UI only, keep logic elsewhere unchanged */}
      {false && (
        <div className={`flex gap-2 mt-3 flex-wrap ${lang === 'ar' ? 'justify-end' : 'justify-start'}`}>
          {/* Deprecated action set retained off for reference */}
        </div>
      )}
    </div>
  );
};

export default OrderCard; 