import { useState, useEffect, useMemo } from 'react';
import Tabs from '../components/Tabs';
import OrderCard from '../components/OrderCard';
import LanguageSwitcher from '../components/LanguageSwitcher';
import MapView, { type Captain } from '../components/MapView';
import api from '../lib/api';
import { getOrdersByStatus } from '../services/ordersApi';

const translations = {
  ar: {
    dashboardTitle: 'لوحة التحكم - الطلبات',
    tabs: [
      { title: 'قيد الانتظار', status: 'pending' },
      { title: 'تعيين كابتن', status: 'accepted' },
      { title: 'معالجة', status: 'processing' },
      { title: 'انتظار الموافقة', status: 'waiting_restaurant_acceptance' },
      { title: 'مؤجل', status: 'delayed' },
      { title: 'خرج للتوصيل', status: 'out_for_delivery' },
      { title: 'تم التوصيل', status: 'delivered' },
      { title: 'ملغي', status: 'cancelled' },
      { title: 'مشكلة', status: 'issue' },
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
  },
  en: {
    dashboardTitle: 'Orders Dashboard',
    tabs: [
      { title: 'Pending', status: 'pending' },
      { title: 'Captain Assigned', status: 'accepted' },
      { title: 'Processing', status: 'processing' },
      { title: 'Waiting Approval', status: 'waiting_restaurant_acceptance' },
      { title: 'Delayed', status: 'delayed' },
      { title: 'Out for Delivery', status: 'out_for_delivery' },
      { title: 'Delivered', status: 'delivered' },
      { title: 'Cancelled', status: 'cancelled' },
      { title: 'Issue', status: 'issue' },
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
  },
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('pending');
  const [lang, setLang] = useState<'ar' | 'en'>('ar');
  const [orders, setOrders] = useState<any[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const t = translations[lang];

  useEffect(() => {
    api.orders
      .counts()
      .then((data) => setCounts(data))
      .catch(() => {});
  }, [lang]);

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
      const st = String(o.status || '').toLowerCase();
      if (activeTab === 'issue') return st === 'issue';
      if (activeTab === 'delayed') return st === 'delayed';
      return st === activeTab;
    });
  }, [orders, activeTab]);

  const dummyCaptains: Captain[] = [
    { id: 'c1', name: lang === 'ar' ? 'الكابتن أحمد' : 'Captain Ahmad', coords: { lat: 33.516, lng: 36.277 }, orders: 2, dest: lang === 'ar' ? 'مطعم باب الحارة' : 'Bab Al Hara' },
    { id: 'c2', name: lang === 'ar' ? 'الكابتن سامر' : 'Captain Samer', coords: { lat: 33.514, lng: 36.279 }, orders: 1, dest: lang === 'ar' ? 'مطعم الشام' : 'Al Sham' },
    { id: 'c3', name: lang === 'ar' ? 'الكابتن ليلى' : 'Captain Layla', coords: { lat: 33.518, lng: 36.274 }, orders: 0, dest: '' },
  ];

  return (
    <div className={`w-screen min-h-screen bg-gray-100 overflow-y-auto ${lang === 'ar' ? 'text-right' : 'text-left'}`}
      dir={lang === 'ar' ? 'rtl' : 'ltr'}>
      <div className="max-w-full px-4 py-8 mx-auto">
        <h1 className="text-2xl font-bold text-purple-800 mb-8">{t.dashboardTitle}</h1>
        <LanguageSwitcher currentLang={lang} onSwitch={setLang} />
        <Tabs
          tabs={t.tabs.map((section) => ({
            label: `${section.title} (${getCount(section.status)})`,
            value: section.status,
          }))}
          active={activeTab}
          onChange={setActiveTab}
          dir={lang === 'ar' ? 'rtl' : 'ltr'}
        />
        {activeTab === 'accepted' ? (
          <>
            <MapView
              customerLocation={visibleOrders[0]?.customerLocation}
              restaurantLocation={visibleOrders[0]?.restaurantLocation}
              captains={dummyCaptains}
            />
            <div className="flex flex-col gap-4 mt-4">
              {loading ? (
                <div className="text-center text-gray-400 py-8">{t.loading}</div>
              ) : error ? (
                <div className="text-center text-red-500 py-8">{t.error}</div>
              ) : visibleOrders.length === 0 ? (
                <div className="text-center text-gray-400 py-8">{t.noOrders}</div>
              ) : (
                visibleOrders.map((order) => {
                  return <OrderCard key={order.order_id} {...order} lang={lang} />;
                })
              )}
            </div>
          </>
        ) : activeTab === 'processing' ? (
          <div className={`w-full flex flex-col ${lang === 'ar' ? 'lg:flex-row-reverse' : 'lg:flex-row'} gap-6 mt-4`}>
            {t.processingSubstages.map((sub) => {
              const subOrders = visibleOrders.filter((order) => order.substage === sub.key);
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
                      {subOrders.map((order) => {
                        return <OrderCard key={order.order_id} {...order} lang={lang} />;
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col gap-4 mt-4">
            {loading ? (
              <div className="text-center text-gray-400 py-8">{t.loading}</div>
            ) : error ? (
              <div className="text-center text-red-500 py-8">{t.error}</div>
            ) : visibleOrders.length === 0 ? (
              <div className="text-center text-gray-400 py-8">{t.noOrders}</div>
            ) : (
              visibleOrders.map((order) => {
                return <OrderCard key={order.order_id} {...order} lang={lang} />;
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
}
