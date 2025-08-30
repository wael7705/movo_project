import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { subscribeTabNotify } from '../realtime/notify';
import GlassToast from '../components/GlassToast';
import Tabs from '../components/Tabs';
import OrderCard from '../components/OrderCard';
import LanguageSwitcher from '../components/LanguageSwitcher';
import MapView, { type Captain } from '../components/MapView';
import AssignCaptainView from '../features/assign/AssignCaptainView';
import api from '../lib/api';
import { getOrdersByStatus } from '../services/ordersApi';

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const translations = {
  ar: {
    dashboardTitle: 'لوحة التحكم - الطلبات',
    tabs: [
      { title: 'قيد الانتظار', status: 'pending' },
      { title: 'تعيين كابتن', status: 'choose_captain' },
      { title: 'معالجة', status: 'processing' },
      { title: 'خرج للتوصيل', status: 'out_for_delivery' },
      { title: 'تم التوصيل', status: 'delivered' },
      { title: 'ملغي', status: 'cancelled' },
      { title: 'مشكلة', status: 'problem' },
      { title: 'مؤجل', status: 'deferred' },
      
    ],
    processingSubstages: [
      { key: 'waiting_approval', label: 'انتظار الموافقة' },
      { key: 'preparing', label: 'التحضير' },
      { key: 'captain_received', label: 'الكابتن استلم' },
    ],
    noOrders: 'لا توجد طلبات حالياً.',
    order: 'طلب',
    loading: '...جاري التحميل',
    error: 'حدث خطأ أثناء جلب الطلبات',
    showMap: 'عرض الخريطة',
    closeMap: 'إغلاق الخريطة',
    createDemoOrder: 'إنشاء طلب وهمي',
    createProcessingOrder: 'إنشاء طلب معالج',
  },
  en: {
    dashboardTitle: 'Orders Dashboard',
    tabs: [
      { title: 'Pending', status: 'pending' },
      { title: 'Captain Selection', status: 'choose_captain' },
      { title: 'Processing', status: 'processing' },
      { title: 'Out for Delivery', status: 'out_for_delivery' },
      { title: 'Delivered', status: 'delivered' },
      { title: 'Cancelled', status: 'cancelled' },
      { title: 'Problem', status: 'problem' },
      { title: 'Deferred', status: 'deferred' },
      
    ],
    processingSubstages: [
      { key: 'waiting_approval', label: 'Waiting Approval' },
      { key: 'preparing', label: 'Preparing' },
      { key: 'captain_received', label: 'Captain Received' },
    ],
    noOrders: 'No orders currently.',
    order: 'order',
    loading: 'Loading...',
    error: 'Error fetching orders',
    showMap: 'Show Map',
    closeMap: 'Close Map',
    createDemoOrder: 'Create Demo Order',
    createProcessingOrder: 'Create Processing Order',
  },
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('pending');
  const { tab } = useParams();
  const navigate = useNavigate();
  const [lang, setLang] = useState<'ar' | 'en'>('ar');
  const [orders, setOrders] = useState<any[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{open:boolean; title:string; message:string; level?:'info'|'success'|'warning'|'error'}>({open:false, title:'', message:''});
  
  // Initialize from URL (?tab=...) and listen to back/forward
  useEffect(() => {
    const map: Record<string, string> = { assign: 'choose_captain', issue: 'problem' };
    const applyFromURL = () => {
      const params = new URLSearchParams(window.location.search);
      const q = ((tab as string) || params.get('tab') || '').trim().toLowerCase();
      if (q) setActiveTab(map[q] ?? q);
    };
    applyFromURL();
    const onPop = () => applyFromURL();
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, [tab]);
  const t = translations[lang];

  useEffect(() => {
    api.orders
      .counts()
      .then((data) => setCounts(data))
      .catch(() => {});
  }, [lang]);

  useEffect(() => {
    const unsubscribe = subscribeTabNotify(activeTab, (msg: any) => {
      const text = typeof msg === 'string' ? msg : (msg?.message ?? '');
      if (text) setToast({ open: true, title: 'Notification', message: text, level: 'success' });
    });
    return () => {
      if (typeof unsubscribe === 'function') unsubscribe();
    };
  }, [activeTab]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getOrdersByStatus(activeTab)
      .then((data) => setOrders(data))
      .catch(() => setError(t.error))
      .finally(() => setLoading(false));
  }, [activeTab, lang]);

  const getCount = (status: string) => counts[status] ?? 0;

  const visibleOrders = useMemo(() => {
    return orders.filter((o) => {
      const st = String(o.current_status || o.status || '').toLowerCase();
      if (activeTab === 'problem') return st === 'problem';
      if (activeTab === 'cancelled') return st === 'cancelled';
      return st === activeTab;
    });
  }, [orders, activeTab]);

  const createDemoOrder = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BASE}/orders/demo`, {
        method: 'POST',
      });
      if (response.ok) {
        // إعادة تحميل الطلبات
        const data = await getOrdersByStatus(activeTab);
        setOrders(data);
        // تحديث العدادات
        api.orders.counts().then((data) => setCounts(data));
      }
    } catch (error) {
      console.error('Error creating demo order:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (orderId: number, newStatus: string) => {
    try {
      setLoading(true);
      if (newStatus === 'cancelled') {
        await api.orders.cancel(orderId);
      } else if (newStatus === 'problem') {
        await api.orders.updateStatus(orderId, 'problem');
      } else {
        // نوحّد كل الأزرار التي تعني الانتقال إلى التالي تحت /next
        await api.orders.next(orderId);
      }
      // حدث القائمة والعدادات دون تغيير التبويب الحالي
      const [data, cnt] = await Promise.all([
        getOrdersByStatus(activeTab),
        api.orders.counts(),
      ]);
      setOrders(data);
      setCounts(cnt);
    } catch (e) {
      setError(t.error);
    } finally {
      setLoading(false);
    }
  };

  const createProcessingOrder = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BASE}/orders/demo/processing`, {
        method: 'POST',
      });
      if (response.ok) {
        // إعادة تحميل الطلبات
        const data = await getOrdersByStatus(activeTab);
        setOrders(data);
        // تحديث العدادات
        api.orders.counts().then((data) => setCounts(data));
      }
    } catch (error) {
      console.error('Error creating processing order:', error);
    } finally {
      setLoading(false);
    }
  };

  const dummyCaptains: Captain[] = [
    { id: 'c1', name: lang === 'ar' ? 'الكابتن أحمد' : 'Captain Ahmad', coords: { lat: 33.516, lng: 36.277 }, orders: 2, dest: lang === 'ar' ? 'مطعم باب الحارة' : 'Bab Al Hara' },
    { id: 'c2', name: lang === 'ar' ? 'الكابتن سامر' : 'Captain Samer', coords: { lat: 33.514, lng: 36.279 }, orders: 1, dest: lang === 'ar' ? 'مطعم الشام' : 'Al Sham' },
    { id: 'c3', name: lang === 'ar' ? 'الكابتن ليلى' : 'Captain Layla', coords: { lat: 33.518, lng: 36.274 }, orders: 0, dest: '' },
  ];

  return (
    <div className={`w-screen min-h-screen bg-gray-100 overflow-y-auto ${lang === 'ar' ? 'text-right' : 'text-left'}`}
      dir={lang === 'ar' ? 'rtl' : 'ltr'}>
      <div className="max-w-full px-4 py-8 mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-purple-800">{t.dashboardTitle}</h1>
          <a href="/supervisor" className="text-sm text-violet-700 hover:underline">Go to Supervisor ▸</a>
        </div>
        <LanguageSwitcher currentLang={lang} onSwitch={setLang} />
        
        {/* أزرار إنشاء الطلبات الوهمية */}
        <div className={`flex gap-4 mb-6 ${lang === 'ar' ? 'justify-end' : 'justify-start'}`}>
          <button
            onClick={createDemoOrder}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {t.createDemoOrder}
          </button>
          <button
            onClick={createProcessingOrder}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {t.createProcessingOrder}
          </button>
        </div>

        <Tabs
          tabs={t.tabs.map((section) => ({
            label: `${section.title} (${getCount(section.status)})`,
            value: section.status,
          }))}
          active={activeTab}
          onChange={(v)=>{
            setActiveTab(v);
            const rev: Record<string,string> = { choose_captain:'assign', problem:'issue' };
            const slug = rev[v] ?? v;
            navigate(`/t/${slug}`, { replace: false });
          }}
          dir={lang === 'ar' ? 'rtl' : 'ltr'}
        />
        
        {activeTab === 'choose_captain' ? (
          <>
            {/* خريطة ترشيح الكباتن بكامل العرض */}
            <AssignCaptainView
              orderId={visibleOrders[0]?.order_id ?? 0}
              restaurant={{
                lat: visibleOrders[0]?.restaurantLocation?.lat ?? 33.5138,
                lng: visibleOrders[0]?.restaurantLocation?.lng ?? 36.2765,
              }}
              customer={{
                lat: visibleOrders[0]?.customerLocation?.lat ?? 33.515,
                lng: visibleOrders[0]?.customerLocation?.lng ?? 36.28,
              }}
              onAssigned={async () => {
                const [data, cnt] = await Promise.all([
                  getOrdersByStatus(activeTab),
                  api.orders.counts(),
                ]);
                setOrders(data);
                setCounts(cnt);
              }}
            />
            <div className="flex flex-col gap-4 mt-4">
              {loading ? (
                <div className="text-center text-gray-400 py-8">{t.loading}</div>
              ) : error ? (
                <div className="text-center text-red-500 py-8">{t.error}</div>
              ) : visibleOrders.length === 0 ? (
                <div className="text-center text-gray-400 py-8">{t.noOrders}</div>
              ) : (
                visibleOrders.map((order) => (
                  <OrderCard
                    key={order.order_id}
                    {...order}
                    lang={lang}
                    current_tab={activeTab}
                    onStatusChange={handleStatusChange}
                  />
                ))
              )}
            </div>
          </>
        ) : activeTab === 'processing' ? (
          <div className={`w-full flex flex-col ${lang === 'ar' ? 'lg:flex-row-reverse' : 'lg:flex-row'} gap-6 mt-4`}>
            {/* Debug info */}
            <div className="w-full mb-4 p-4 bg-gray-100 rounded-lg">
              <h3 className="font-bold mb-2">🔍 معلومات التصحيح:</h3>
              <p>إجمالي الطلبات: {visibleOrders.length}</p>
              <p>الطلبات في حالة processing: {visibleOrders.filter(o => o.current_status === 'processing').length}</p>
              <div className="mt-2">
                <p className="font-semibold">تفاصيل الطلبات:</p>
                {visibleOrders.map((order, index) => (
                  <div key={index} className="text-sm text-gray-600">
                    الطلب #{order.order_id}: status={order.status}, current_status={order.current_status}, substage={order.substage}
                  </div>
                ))}
              </div>
            </div>
            
            {t.processingSubstages.map((sub) => {
              const subOrders = visibleOrders.filter((order) => {
                // تأكد من أن الطلب في حالة processing
                if (order.current_status !== 'processing') return false;
                
                // تطابق substage
                return order.substage === sub.key;
              });
              
              return (
                <div key={sub.key} className="flex-1 min-w-[260px]">
                  <div className="font-bold text-lg mb-2 flex justify-between items-center">
                    <span>{sub.label}</span>
                    <span className="bg-gray-800 text-white rounded-full px-3 py-1 text-sm font-bold">{subOrders.length} {t.order}</span>
                  </div>
                  {loading ? (
                    <div className="text-center text-gray-400 py-8">{t.loading}</div>
                  ) : error ? (
                    <div className="text-center text-red-500 py-8">{t.error}</div>
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
                        />
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col gap-4 mt-4">
            {activeTab === 'out_for_delivery' && (
              <MapView
                customerLocation={visibleOrders[0]?.customerLocation}
                restaurantLocation={visibleOrders[0]?.restaurantLocation}
                captains={dummyCaptains}
                lang={lang}
                mode="track"
              />
            )}
            {loading ? (
              <div className="text-center text-gray-400 py-8">{t.loading}</div>
            ) : error ? (
              <div className="text-center text-red-500 py-8">{t.error}</div>
            ) : visibleOrders.length === 0 ? (
              <div className="text-center text-gray-400 py-8">{t.noOrders}</div>
            ) : (
              visibleOrders.map((order) => (
                <OrderCard
                  key={order.order_id}
                  {...order}
                  lang={lang}
                  current_tab={activeTab}
                  onStatusChange={handleStatusChange}
                />
              ))
            )}
          </div>
        )}
      </div>
      <GlassToast open={toast.open} onClose={()=>setToast(t=>({ ...t, open:false }))} title={toast.title} message={toast.message} level={toast.level} position={lang==='ar' ? 'left' : 'right'} />
    </div>
  );
}
