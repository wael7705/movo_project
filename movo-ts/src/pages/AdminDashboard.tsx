import { useState, useEffect } from 'react';
import Tabs from '../components/Tabs';
import OrderCard from '../components/OrderCard';
import LanguageSwitcher from '../components/LanguageSwitcher';
import OrderMap from '../components/OrderMap';
import { type Captain } from '../components/MapView';
import api from '../lib/api';

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

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.orders
      .list({ order_status: activeTab })
      .then((data) => setOrders(Array.isArray(data) ? data : []))
      .catch(() => setError(lang === 'ar' ? 'حدث خطأ أثناء جلب الطلبات' : 'Error fetching orders'))
      .finally(() => setLoading(false));
  }, [activeTab, lang]);

  // Handler functions for order actions
  const handleStatusChange = async (orderId: number, newStatus: string) => {
    try {
      if (newStatus === 'cancelled') {
        await api.orders.cancel(orderId);
        setActiveTab('cancelled');
        const data = await api.orders.list({ order_status: 'cancelled' });
        setOrders(data);
        return;
      }

      // Use strict NEXT flow regardless of UI sub-stages
      await api.orders.next(orderId);
      const nextTabMap: Record<string, string> = {
        pending: 'captain_assigned',
        captain_assigned: 'processing',
        processing: 'out_for_delivery',
        out_for_delivery: 'delivered',
      };
      const nextTab = nextTabMap[activeTab] || activeTab;
      setActiveTab(nextTab);
      const data = await api.orders.list({ order_status: nextTab });
      setOrders(data);
    } catch (err) {
      console.error('Failed to update order status:', err);
    }
  };

  const handleInvoice = (orderId: number) => {
    console.log(`Invoice for order ${orderId}`);
  };

  const handleNotes = (orderId: number) => {
    console.log(`Notes for order ${orderId}`);
  };

  const handleTrack = (orderId: number) => {
    console.log(`Track order ${orderId}`);
  };

  const handleRate = (orderId: number) => {
    console.log(`Rate order ${orderId}`);
  };

  const handleCreateDemoOrder = async () => {
    try {
      await api.orders.createDemo();
      // بعد الإنشاء يجب أن يبدأ الطلب من pending وفق قاعدة البيانات
      setActiveTab('pending');
      const data = await api.orders.list({ order_status: 'pending' });
      setOrders(data);
    } catch (err) {
      console.error('Failed to create demo order:', err);
    }
  };

  // مثال: يمكن لاحقًا جلب بيانات الكباتن من API
  const dummyCaptains: Captain[] = [
    { id: 'c1', name: lang === 'ar' ? 'الكابتن أحمد' : 'Captain Ahmad', coords: { lat: 33.516, lng: 36.277 }, orders: 2, dest: lang === 'ar' ? 'مطعم باب الحارة' : 'Bab Al Hara' },
    { id: 'c2', name: lang === 'ar' ? 'الكابتن سامر' : 'Captain Samer', coords: { lat: 33.514, lng: 36.279 }, orders: 1, dest: lang === 'ar' ? 'مطعم الشام' : 'Al Sham' },
    { id: 'c3', name: lang === 'ar' ? 'الكابتن ليلى' : 'Captain Layla', coords: { lat: 33.518, lng: 36.274 }, orders: 0, dest: '' },
  ];

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
          tabs={([
            { title: lang === 'ar' ? 'قيد الانتظار' : 'Pending', status: 'pending' },
            { title: lang === 'ar' ? 'اختيار كابتن' : 'Select Captain', status: 'captain_assigned' },
            { title: lang === 'ar' ? 'معالجة' : 'Processing', status: 'processing' },
            { title: lang === 'ar' ? 'مؤجل' : 'Delayed', status: 'delayed' },
            { title: lang === 'ar' ? 'خرج للتوصيل' : 'Out for Delivery', status: 'out_for_delivery' },
            { title: lang === 'ar' ? 'تم التوصيل' : 'Delivered', status: 'delivered' },
            { title: lang === 'ar' ? 'ملغي' : 'Cancelled', status: 'cancelled' },
            { title: lang === 'ar' ? 'مشكلة' : 'Issue', status: 'issue' },
          ]).map((section) => ({ label: section.title, value: section.status }))}
          active={activeTab}
          onChange={setActiveTab}
          dir={lang === 'ar' ? 'rtl' : 'ltr'}
        />
        {activeTab === 'captain_assigned' ? (
          <>
            <OrderMap
              mode="select"
              customerLocation={orders[0]?.customerLocation}
              restaurantLocation={orders[0]?.restaurantLocation}
              captains={dummyCaptains}
              onCaptainSelect={(captainId) => {
                console.log(`Selected captain: ${captainId}`);
              }}
            />
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
                            onStatusChange={handleStatusChange}
                            onInvoice={handleInvoice}
                            onNotes={handleNotes}
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
            <OrderMap
              mode="track"
              customerLocation={orders[0]?.customerLocation}
              restaurantLocation={orders[0]?.restaurantLocation}
              captains={dummyCaptains}
              onTrackOrder={() => {
                console.log('Track order clicked');
              }}
            />
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
        )}
      </div>
    </div>
  );
}
