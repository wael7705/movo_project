import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import { useEffect, useMemo, useState } from 'react';
import { restaurantIcon, customerIcon, captainIcon } from '../../components/map/markers';

export type LatLng = { lat: number; lng: number };

type Candidate = {
  captain_id: number;
  captain_name: string;
  last_lat: number;
  last_lng: number;
  active_orders: number;
  distance_km: number;
  last_order_ids: number[];
};

export default function AssignCaptainView(props: {
  orderId: number;
  restaurant: LatLng;
  customer: LatLng;
  onWaiting?: (captainId: number) => void;
  onAssigned?: () => void;
}) {
  const { orderId, restaurant, customer, onWaiting, onAssigned } = props;
  const [cands, setCands] = useState<Candidate[]>([]);
  const [hoverId, setHoverId] = useState<number | null>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [selectedCaptainId, setSelectedCaptainId] = useState<number | null>(null);

  const center = useMemo(
    () => ({ lat: (restaurant.lat + customer.lat) / 2, lng: (restaurant.lng + customer.lng) / 2 }),
    [restaurant, customer]
  );

  useEffect(() => {
    fetch(`/api/v1/assign/orders/${orderId}/candidates?radius_km=8`)
      .then((r) => r.json())
      .then(setCands)
      .catch(() => setCands([]));
  }, [orderId]);

  // WebSocket محاكاة حركة عند المرور على مرشح
  useEffect(() => {
    if (!hoverId) {
      if (socket) {
        socket.close();
        setSocket(null);
      }
      return;
    }
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${location.host}/ws/captain/${hoverId}`);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg?.type === 'pos') {
          setCands((prev) =>
            prev.map((c) =>
              c.captain_id === hoverId ? { ...c, last_lat: msg.lat, last_lng: msg.lng } : c
            )
          );
        }
      } catch {}
    };
    ws.onclose = () => setSocket(null);
    setSocket(ws);
    return () => ws.close();
  }, [hoverId]);

  const assign = async (cid: number) => {
    onWaiting?.(cid);
    const r = await fetch(`/api/v1/assign/orders/${orderId}/assign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ captain_id: cid }),
    });
    if (!r.ok) return;
    setSelectedCaptainId(cid);
    // افتح WS لمحاكاة "قبول" خلال ثوانٍ ثم call onAssigned + نقل الحالة
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${location.host}/ws/captain/${cid}`);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg?.type === 'accepted' && msg.order_id === orderId) {
          // انقل الطلب للحالة التالية
          fetch(`/api/v1/orders/${orderId}/next`, { method: 'PATCH' })
            .catch(() => {})
            .finally(() => onAssigned?.());
          ws.close();
        }
      } catch {}
    };
    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'assign', order_id: orderId }));
    };
    ws.onclose = () => {};
  };

  return (
    <div className="grid gap-4" style={{ gridTemplateRows: 'auto 60vh auto' }}>
      <div dir="rtl" className="text-purple-800 font-bold text-lg">خريطة اختيار كابتن</div>
      <div className="rounded-2xl overflow-hidden shadow">
        <MapContainer center={[center.lat, center.lng]} zoom={13} style={{ height: '60vh', width: '100%' }}>
          <MapUpdater center={center} />
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Marker position={[restaurant.lat, restaurant.lng]} icon={restaurantIcon}>
            <Popup>
              <b>المطعم</b>
            </Popup>
          </Marker>
          <Marker position={[customer.lat, customer.lng]} icon={customerIcon}>
            <Popup>
              <b>الزبون</b>
            </Popup>
          </Marker>
          <Polyline positions={[[restaurant.lat, restaurant.lng], [customer.lat, customer.lng]]} />
          {selectedCaptainId && (() => {
            const sc = cands.find(x => x.captain_id === selectedCaptainId);
            if (!sc) return null as any;
            return (
              <Polyline color="orange" positions={[[sc.last_lat, sc.last_lng], [restaurant.lat, restaurant.lng], [customer.lat, customer.lng]]} />
            );
          })()}
          {cands.map((c) => (
            <Marker key={c.captain_id} position={[c.last_lat, c.last_lng]} icon={captainIcon(hoverId === c.captain_id)}>
              <Popup>
                <div dir="rtl">
                  <div className="font-bold text-purple-700 mb-1">{c.captain_name}</div>
                  <div className="text-sm">ID: {c.captain_id}</div>
                  <div className="text-sm">المسافة: {c.distance_km} كم</div>
                  <div className="text-sm">طلبات نشطة: {c.active_orders}</div>
                  <div className="text-sm">آخر طلبات: {c.last_order_ids.join(', ')}</div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(auto-fill,minmax(220px,1fr))' }}>
        {cands.map((c) => (
          <div
            key={c.captain_id}
            className="p-3 rounded-xl border shadow-sm bg-white hover:shadow-md transition cursor-pointer"
            onMouseEnter={() => setHoverId(c.captain_id)}
            onMouseLeave={() => setHoverId(null)}
            dir="rtl"
          >
            <div className="font-bold text-slate-800">{c.captain_name}</div>
            <div className="text-xs text-slate-500">ID: {c.captain_id}</div>
            <div className="text-sm mt-1">المسافة: {c.distance_km} كم</div>
            <div className="text-sm">طلبات نشطة: {c.active_orders}</div>
            {c.last_order_ids.length > 0 && (
              <div className="text-xs text-slate-500">آخر طلبات: {c.last_order_ids.join(', ')}</div>
            )}
            <button onClick={() => assign(c.captain_id)} className="mt-2 w-full bg-emerald-600 text-white rounded-lg py-1 text-sm hover:bg-emerald-700">
              اختيار الكابتن
            </button>
          </div>
        ))}
        {cands.length === 0 && <div className="opacity-70" dir="rtl">لا يوجد مرشحون ضمن النطاق الحالي.</div>}
      </div>
    </div>
  );
}

function MapUpdater({ center }: { center: LatLng }) {
  const map = useMap();
  useEffect(() => {
    map.setView([center.lat, center.lng], map.getZoom(), { animate: true });
  }, [center.lat, center.lng]);
  return null;
}

