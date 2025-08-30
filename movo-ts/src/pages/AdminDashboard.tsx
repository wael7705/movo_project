import { useState, useEffect } from 'react';
import Tabs from '../components/Tabs';
import OrderCard from '../components/OrderCard';
import LanguageSwitcher from '../components/LanguageSwitcher';
import AssignCaptainView from '../features/assign/AssignCaptainView';
import api from '../lib/api';
import OutForDeliveryView from '../features/delivery/OutForDeliveryView';
import NotesModal from '../components/NotesModal';
import GlassToast from '../components/GlassToast';

const translations = {
  ar: {
    dashboardTitle: 'لوحة التحكم - الطلبات',
    processingSubstages: [
      { key: 'waiting_approval', label: 'انتظار الموافقة' },
      { key: 'preparing', label: 'التحضير' },
      { key: 'captain_received', label: 'الكابتن استلم' },
    ],
    noOrders: 'لا توجد طلبات حالياً.',
    order: 'طلب',
  },
  en: {
    dashboardTitle: 'Orders Dashboard',
    processingSubstages: [
      { key: 'waiting_approval', label: 'Waiting Approval' },
      { key: 'preparing', label: 'Preparing' },
      { key: 'captain_received', label: 'Captain Received' },
    ],
    noOrders: 'No orders currently.',
    order: 'order',
  },
};

type Order = any;

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('pending');
  const [lang, setLang] = useState<'ar' | 'en'>('ar');
  const t = translations[lang];
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [selectedOrderId, setSelectedOrderId] = useState<number | null>(null);
  const [awaitingOrders, setAwaitingOrders] = useState<Record<number, boolean>>({});
  const [trackedOrderId, setTrackedOrderId] = useState<number | null>(null);
  const [notesForOrderId, setNotesForOrderId] = useState<number | null>(null);
  const [ordersWithNotes, setOrdersWithNotes] = useState<Record<number, boolean>>({});
  const [toast, setToast] = useState<{open:boolean; title:string; message:string; level?:'info'|'success'|'warning'|'error'}>({open:false, title:'', message:''});

  const sections = ([
    { title: lang === 'ar' ? 'قيد الانتظار' : 'Pending', status: 'pending' },
    { title: lang === 'ar' ? 'تعيين كابتن' : 'Captain Selection', status: 'choose_captain' },
    { title: lang === 'ar' ? 'معالجة' : 'Processing', status: 'processing' },
    { title: lang === 'ar' ? 'خرج للتوصيل' : 'Out for Delivery', status: 'out_for_delivery' },
    { title: lang === 'ar' ? 'تم التوصيل' : 'Delivered', status: 'delivered' },
    { title: lang === 'ar' ? 'ملغي' : 'Cancelled', status: 'cancelled' },
    { title: lang === 'ar' ? 'مشكلة' : 'Problem', status: 'problem' },
    { title: lang === 'ar' ? 'مؤجل' : 'Deferred', status: 'deferred' },
  ]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.orders
      .list({ order_status: activeTab })
      .then((data) => setOrders(Array.isArray(data) ? data : []))
      .catch(() => setError(lang === 'ar' ? 'حدث خطأ أثناء جلب الطلبات' : 'Error fetching orders'))
      .finally(() => setLoading(false));
  }, [activeTab, lang]);

  useEffect(() => {
    api.orders.counts().then(setCounts).catch(() => {});
  }, [activeTab, lang]);

  // مزامنة حالة وجود ملاحظات للطلبات الظاهرة بعد التحميل
  useEffect(() => {
    if (!orders || orders.length === 0) return;
    const ids = orders.map(o => o.order_id).join(',');
    fetch(`/api/v1/orders/notes/flags?ids=${ids}`)
      .then(r => (r.ok ? r.json() : {}))
      .then((m) => setOrdersWithNotes(m || {}))
      .catch(() => {});
  }, [orders]);

  // حافظ على طلب مختار لتبويب تعيين كابتن
  useEffect(() => {
    if (activeTab !== 'choose_captain') return;
    if (!orders || orders.length === 0) {
      setSelectedOrderId(null);
      return;
    }
    // إن لم يكن هناك طلب محدد أو تم حذفه من القائمة، اختر الأول
    const exists = selectedOrderId && orders.some(o => o.order_id === selectedOrderId);
    if (!exists) setSelectedOrderId(orders[0].order_id);
  }, [activeTab, orders, selectedOrderId]);

  // Handler functions for order actions
  const handleStatusChange = async (orderId: number, newStatus: string) => {
    try {
      if (newStatus === 'cancelled') {
        await api.orders.cancel(orderId);
      } else if (newStatus === 'problem') {
        await api.orders.updateStatus(orderId, 'problem');
      } else {
        // اتبع مسار next في الباكيند فقط، ولا تغيّر التبويب
        await api.orders.next(orderId);
      }
      // جدّد أوامر التبويب الحالي فقط دون تبديل التبويب
      const [data, cnt] = await Promise.all([
        api.orders.list({ order_status: activeTab }),
        api.orders.counts(),
      ]);
      setOrders(data);
      setCounts(cnt);
      // (اختياري) يمكن تحديث عدادات عامة إذا أردت لاحقاً
    } catch (err) {
      console.error('Failed to update order status:', err);
    }
  };

  const handleInvoice = (orderId: number) => {
    console.log(`Invoice for order ${orderId}`);
  };

  const handleNotes = (orderId: number) => {
    setNotesForOrderId(orderId);
  };

  // عندما يغلق المودال، حدّث الهايلايت إن وُجدت ملاحظات
  const handleNotesClosed = async () => {
    if (!notesForOrderId) {
      setNotesForOrderId(null);
      return;
    }
    try {
      const list = await api.orders.notes.listByOrder(notesForOrderId);
      setOrdersWithNotes((prev) => ({ ...prev, [notesForOrderId]: Array.isArray(list) && list.length > 0 }));
      if (Array.isArray(list) && list.length > 0) {
        setToast({open:true, title: lang==='ar' ? 'تم حفظ الملاحظة' : 'Note Saved', message: `${lang==='ar' ? 'تم حفظ الملاحظة للطلب' : 'Note saved for order'} #${notesForOrderId}`, level:'success'});
      }
    } catch {}
    setNotesForOrderId(null);
  };

  const handleNoteSavedInstant = (note: { orderId: number }) => {
    // فعّل الهايلايت فورًا دون انتظار إغلاق المودال أو إعادة التحميل
    setOrdersWithNotes((prev) => ({ ...prev, [note.orderId]: true }));
    setToast({open:true, title: lang==='ar' ? 'تم حفظ الملاحظة' : 'Note Saved', message: `${lang==='ar' ? 'تم حفظ الملاحظة للطلب' : 'Note saved for order'} #${note.orderId}`, level:'success'});
  };

  const handleTrack = (orderId: number) => {
    setTrackedOrderId(orderId);
    setActiveTab('out_for_delivery');
  };

  const handleRate = (orderId: number) => {
    console.log(`Rate order ${orderId}`);
  };

  const handleCreateDemoOrder = async () => {
    try {
      await api.orders.createDemo();
      // بعد الإنشاء يجب أن يبدأ الطلب من pending وفق قاعدة البيانات
      setActiveTab('pending');
      const [data, cnt] = await Promise.all([
        api.orders.list({ order_status: 'pending' }),
        api.orders.counts(),
      ]);
      setOrders(data);
      setCounts(cnt);
    } catch (err) {
      console.error('Failed to create demo order:', err);
    }
  };

  return (
    <div className={`w-screen min-h-screen bg-gray-100 overflow-y-auto ${lang === 'ar' ? 'text-right' : 'text-left'}`}
      dir={lang === 'ar' ? 'rtl' : 'ltr'}>
      <div className="max-w-full px-4 py-8 mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-purple-800">{t.dashboardTitle}</h1>
          <button 
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
            onClick={handleCreateDemoOrder}
          >
            {lang === 'ar' ? 'إنشاء طلب وهمي' : 'Create Dummy Order'}
          </button>
        </div>
        <LanguageSwitcher currentLang={lang} onSwitch={setLang} />
        <Tabs
          tabs={sections.map((s) => ({ label: `${s.title} (${counts[s.status] ?? 0})`, value: s.status }))}
          active={activeTab}
          onChange={setActiveTab}
          dir={lang === 'ar' ? 'rtl' : 'ltr'}
        />
        {activeTab === 'choose_captain' ? (
          <>
            {(() => {
              const sel = orders.find(o => o.order_id === selectedOrderId) ?? orders[0];
              const rest = sel?.restaurantLocation ?? { lat: 33.5138, lng: 36.2765 };
              const cust = sel?.customerLocation ?? { lat: 33.515, lng: 36.28 };
              return (
                <AssignCaptainView
                  orderId={sel?.order_id ?? 0}
                  restaurant={{ lat: rest?.lat ?? 33.5138, lng: rest?.lng ?? 36.2765 }}
                  customer={{ lat: cust?.lat ?? 33.515, lng: cust?.lng ?? 36.28 }}
                  onWaiting={() => {
                    if (!sel?.order_id) return;
                    setAwaitingOrders(prev => ({ ...prev, [sel.order_id]: true }));
                  }}
                  onAssigned={async () => {
                    // عند القبول: أزل حالة الانتظار وجدد البيانات
                    if (sel?.order_id) {
                      setAwaitingOrders(prev => {
                        const copy = { ...prev };
                        delete copy[sel.order_id as number];
                        return copy;
                      });
                    }
                    const [data, cnt] = await Promise.all([
                      api.orders.list({ order_status: activeTab }),
                      api.orders.counts(),
                    ]);
                    setOrders(data);
                    setCounts(cnt);
                    // في حال انتقال الطلب، اختر أول طلب متاح في تبويب تعيين كابتن
                    if (activeTab === 'choose_captain') {
                      if (data.length > 0) setSelectedOrderId(data[0].order_id);
                      else setSelectedOrderId(null);
                    }
                  }}
                />
              );
            })()}
            <div className="flex flex-col gap-4 mt-4">
              {loading ? (
                <div className="text-center text-gray-400 py-8">{lang === 'ar' ? '...جاري التحميل' : 'Loading...'}</div>
              ) : error ? (
                <div className="text-center text-red-500 py-8">{error}</div>
              ) : orders.length === 0 ? (
                <div className="text-center text-gray-400 py-8">{t.noOrders}</div>
              ) : (
                orders.map((order) => (
                  <OrderCard 
                    key={order.order_id} 
                    {...order} 
                    lang={lang}
                    status={(order as any).status ?? activeTab}
                    current_tab={activeTab}
                    awaitingCaptain={!!awaitingOrders[order.order_id]}
                    notesHighlight={!!ordersWithNotes[order.order_id]}
                    onAssignCaptainClick={(oid)=> {
                      setActiveTab('choose_captain');
                      setSelectedOrderId(oid);
                    }}
                    onStatusChange={handleStatusChange}
                    onInvoice={handleInvoice}
                    onNotes={handleNotes}
                    onTrack={handleTrack}
                    onRate={handleRate}
                  />
                ))
              )}
            </div>
          </>
        ) : activeTab === 'processing' ? (
          <>
            <div className="bg-gray-800 text-white rounded-lg p-3 mb-4 text-center">
              <span className="font-bold text-lg">{orders.length} {t.order}</span>
            </div>
            <div className={`w-full flex flex-col ${lang === 'ar' ? 'lg:flex-row-reverse' : 'lg:flex-row'} gap-6 mt-4`}>
              {t.processingSubstages.map((sub) => {
                const subOrders = orders.filter((order) => order.substage === sub.key);
                return (
                  <div key={sub.key} className="flex-1 min-w-[260px]">
                    <div className="font-bold text-lg mb-2 flex justify-between items-center">
                      <span>{sub.label}</span>
                      <span className="bg-gray-800 text-white rounded-full px-3 py-1 text-sm font-bold">{subOrders.length} {t.order}</span>
                    </div>
                    {loading ? (
                      <div className="text-center text-gray-400 py-8">{lang === 'ar' ? '...جاري التحميل' : 'Loading...'}</div>
                    ) : error ? (
                      <div className="text-center text-red-500 py-8">{error}</div>
                    ) : subOrders.length === 0 ? (
                      <div className="bg-blue-900 text-blue-100 rounded-lg p-4 text-center text-sm">{t.noOrders}</div>
                    ) : (
                      <div className="flex flex-col gap-4">
                        {subOrders.map((order) => (
                          <OrderCard 
                            key={order.order_id} 
                            {...order} 
                            lang={lang}
                            current_tab={activeTab}
                            onStatusChange={handleStatusChange}
                            onInvoice={handleInvoice}
                            onNotes={handleNotes}
                            notesHighlight={!!ordersWithNotes[order.order_id]}
                            onTrack={handleTrack}
                            onRate={handleRate}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        ) : activeTab === 'out_for_delivery' ? (
          <>
            {(() => {
              const sel = trackedOrderId ? orders.find(o => o.order_id === trackedOrderId) : orders[0];
              const rest = sel?.restaurantLocation ?? { lat: 33.5138, lng: 36.2765 };
              const cust = sel?.customerLocation ?? { lat: 33.515, lng: 36.28 };
              const capId = sel?.captain_id ?? null;
              return (
                <OutForDeliveryView
                  orderId={sel?.order_id ?? 0}
                  restaurant={{ lat: rest?.lat ?? 33.5138, lng: rest?.lng ?? 36.2765 }}
                  customer={{ lat: cust?.lat ?? 33.515, lng: cust?.lng ?? 36.28 }}
                  captainId={capId}
                  onDelivered={async () => {
                    await api.orders.next(sel?.order_id ?? 0);
                    // حدث عدادات وقوائم
                    const [data, cnt] = await Promise.all([
                      api.orders.list({ order_status: activeTab }),
                      api.orders.counts(),
                    ]);
                    setOrders(data);
                    setCounts(cnt);
                    // انقل المستخدم تلقائياً إلى تبويب تم التوصيل
                    setActiveTab('delivered');
                  }}
                />
              );
            })()}
            <div className="flex flex-col gap-4 mt-4">
              {loading ? (
                <div className="text-center text-gray-400 py-8">{lang === 'ar' ? '...جاري التحميل' : 'Loading...'}</div>
              ) : error ? (
                <div className="text-center text-red-500 py-8">{error}</div>
              ) : orders.length === 0 ? (
                <div className="text-center text-gray-400 py-8">{t.noOrders}</div>
              ) : (
                orders.map((order) => (
                  <OrderCard 
                    key={order.order_id} 
                    {...order} 
                    lang={lang}
                    status={(order as any).status ?? activeTab}
                    current_tab={activeTab}
                    onStatusChange={handleStatusChange}
                    onInvoice={handleInvoice}
                    onNotes={handleNotes}
                    notesHighlight={!!ordersWithNotes[order.order_id]}
                    onTrack={handleTrack}
                    onRate={handleRate}
                  />
                ))
              )}
            </div>
          </>
        ) : (
          <>
            <div className="bg-gray-800 text-white rounded-lg p-3 mb-4 text-center">
              <span className="font-bold text-lg">{orders.length} {t.order}</span>
            </div>
            <div className="flex flex-col gap-4 mt-4">
              {loading ? (
                <div className="text-center text-gray-400 py-8">{lang === 'ar' ? '...جاري التحميل' : 'Loading...'}</div>
              ) : error ? (
                <div className="text-center text-red-500 py-8">{error}</div>
              ) : orders.length === 0 ? (
                <div className="text-center text-gray-400 py-8">{t.noOrders}</div>
              ) : (
                orders.map((order) => (
                  <OrderCard 
                    key={order.order_id} 
                    {...order} 
                    lang={lang}
                    status={(order as any).status ?? activeTab}
                    current_tab={activeTab}
                    onStatusChange={handleStatusChange}
                    onInvoice={handleInvoice}
                    onNotes={handleNotes}
                    notesHighlight={!!ordersWithNotes[order.order_id]}
                    onTrack={handleTrack}
                    onRate={handleRate}
                  />
                ))
              )}
            </div>
          </>
        )}
        {/* Notes Modal */}
        <NotesModal orderId={notesForOrderId ?? 0} open={!!notesForOrderId} onClose={handleNotesClosed} lang={lang} onSaved={handleNoteSavedInstant} />
        <GlassToast open={toast.open} onClose={()=>setToast(t=>({...t,open:false}))} title={toast.title} message={toast.message} level={toast.level} position={lang==='ar' ? 'left' : 'right'} />
      </div>
    </div>
  );
}
