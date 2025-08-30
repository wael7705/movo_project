import { useEffect, useMemo, useRef, useState } from 'react';
import MapPanel, { type MapPanelRef } from './MapPanel';
import { getCaptainsLive, getRestaurants, toggleRestaurant, getRestaurantStats } from './api';
import { asArray } from '../utils/asArray';

type Restaurant = { id: number; name: string; lat: number; lng: number; visible?: boolean };
type Captain = { id: number; name: string; lat: number; lng: number; status?: 'active'|'busy'|'offline'; orders_now?: number; delivered_today?: number; vehicle?: string; rating?: number };

export default function AdminAnalytics() {
  const [tab, setTab] = useState<'restaurants' | 'captains' | 'employees'>('restaurants');

  return (
    <div>
      <div className="mb-4 flex gap-2">
        {(
          [
            { k: 'restaurants', l: 'Restaurants' },
            { k: 'captains', l: 'Captains' },
            { k: 'employees', l: 'Employees' },
          ] as const
        ).map((t) => (
          <button
            key={t.k}
            onClick={() => setTab(t.k)}
            className={`px-3 py-2 rounded-lg ${tab === t.k ? 'bg-violet-600 text-white' : 'bg-white border hover:bg-zinc-50'}`}
          >
            {t.l}
          </button>
        ))}
      </div>
      {tab === 'restaurants' && <RestaurantsPanel />}
      {tab === 'captains' && <CaptainsPanel />}
      {tab === 'employees' && (
        <div className="p-6 bg-white border rounded-xl">Coming soon…</div>
      )}
    </div>
  );
}

function RestaurantsPanel() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getRestaurants()
      .then((rows) => mounted && setRestaurants(asArray<Restaurant>(rows)))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, []);

  const selected = useMemo(() => restaurants.find((r) => r.id === selectedId) || null, [restaurants, selectedId]);
  const [kpis, setKpis] = useState<{rating:number;orders_today:number;orders_week:number;profit_margin:number}|null>(null);

  const onToggle = async (r: Restaurant, visible: boolean) => {
    await toggleRestaurant(r.id, visible);
    setRestaurants((prev) => prev.map((x) => (x.id === r.id ? { ...x, visible } : x)));
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2">
        <div className="bg-white border rounded-xl">
          {loading && <div className="p-4 text-zinc-500">Loading…</div>}
          {!loading && (
            <ul className="divide-y">
              {Array.isArray(restaurants) && restaurants.map((r) => (
                <li key={r.id} className="p-4">
                  <div className="flex items-center justify-between gap-3">
                    <button className="font-semibold text-zinc-900 hover:text-violet-700 hover:underline flex items-center gap-2" onClick={() => setSelectedId(r.id)}>
                      { (r as any).logoUrl ? (
                        <img src={(r as any).logoUrl} alt={r.name} className="w-6 h-6 rounded-full object-cover" />
                      ) : (
                        <span className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-[10px]">🏪</span>
                      )}
                      <span>{r.name}</span>
                    </button>
                    <label className="inline-flex items-center gap-2 text-sm">
                      <input type="checkbox" checked={!!r.visible} onChange={(e) => onToggle(r, e.target.checked)} />
                      <span className="text-zinc-700">Visible</span>
                    </label>
                  </div>
                  {selectedId === r.id && (
                    <div className="mt-3 text-sm text-zinc-700">
                      <div className="mb-1 font-medium text-zinc-900">Categories</div>
                      <div className="text-zinc-600">(placeholder) Toggle like restaurant</div>
                      <div className="mt-3 mb-1 font-medium text-zinc-900">Addons</div>
                      <div className="text-zinc-600">(placeholder) Toggle like category</div>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      <div>
        <div className="p-4 bg-white border rounded-xl">
          <div className="font-semibold mb-3">KPIs</div>
          {selected ? (
            <KPIs rid={selected.id} onLoad={setKpis} data={kpis} />
          ) : (
            <div className="text-zinc-500 text-sm">Select a restaurant…</div>
          )}
        </div>
      </div>
    </div>
  );
}

function KPIs({ rid, onLoad, data }: { rid:number; onLoad:(d:any)=>void; data:any }){
  useEffect(() => {
    let mounted = true;
    getRestaurantStats(rid).then((d)=>{ if(mounted) onLoad(d); }).catch(()=>{});
    return ()=>{ mounted = false; };
  }, [rid, onLoad]);
  if(!data) return <div className="text-zinc-500 text-sm">Loading…</div>;
  return (
    <div className="text-sm space-y-2">
      <div>Rating: {data.rating?.toFixed?.(1) ?? '—'}</div>
      <div>Orders today: {data.orders_today ?? '—'}</div>
      <div>Orders this week: {data.orders_week ?? '—'}</div>
      <div>Profit margin: {typeof data.profit_margin === 'number' ? `${Math.round(data.profit_margin*100)}%` : '—'}</div>
    </div>
  );
}

function CaptainsPanel() {
  const [captains, setCaptains] = useState<Captain[]>([]);
  const ref = useRef<MapPanelRef>(null);

  useEffect(() => {
    let mounted = true;
    let timer: any;
    const tick = async () => {
      try {
        const rows = await getCaptainsLive();
        if (mounted) setCaptains(Array.isArray(rows) ? rows : []);
      } catch {}
    };
    tick();
    timer = setInterval(tick, 5000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  return (
    <div className="space-y-4">
      <MapPanel ref={ref} captains={captains} />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {captains.map((c) => (
          <div
            key={c.id}
            className="bg-white border rounded-xl p-4 hover:shadow transition"
            onMouseEnter={() => ref.current?.highlightCaptain(c.id)}
          >
            <div className="font-semibold text-zinc-900">{c.name}</div>
            <div className="text-sm text-zinc-600">ID: {c.id} • Vehicle: {c.vehicle || '—'}</div>
            <div className="text-sm">Active: {c.status === 'offline' ? 'No' : 'Yes'}</div>
            <div className="text-sm">Current Orders: {c.orders_now ?? 0}</div>
            <div className="text-sm">Delivered Today: {c.delivered_today ?? 0}</div>
            <div className="text-sm">Rating: {typeof c.rating === 'number' ? c.rating.toFixed(1) : '—'}⭐</div>
          </div>
        ))}
      </div>
    </div>
  );
}


