import { useEffect, useMemo, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import type { LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { restaurantIcon, customerIcon, captainIcon } from '../../components/map/markers';

export default function OutForDeliveryView({
  orderId,
  restaurant,
  customer,
  captainId,
  onDelivered,
}: {
  orderId: number;
  restaurant: { lat: number; lng: number };
  customer: { lat: number; lng: number };
  captainId: number | null | undefined;
  onDelivered?: () => void;
}) {
  const [pos, setPos] = useState<{ lat: number; lng: number } | null>(null);
  const [route, setRoute] = useState<LatLngExpression[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const center = useMemo<{ lat: number; lng: number}>(() => ({
    lat: (restaurant.lat + customer.lat) / 2,
    lng: (restaurant.lng + customer.lng) / 2,
  }), [restaurant, customer]);

  useEffect(() => {
    if (!captainId) return;
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${location.host}/ws/captain/${captainId}`);
    wsRef.current = ws;
    ws.onopen = () => {
      // ابدأ رحلة التوصيل بمسار واضح من المطعم إلى الزبون
      ws.send(JSON.stringify({
        type: 'start_delivery',
        order_id: orderId,
        restaurant,
        customer,
      }));
      setRoute([[restaurant.lat, restaurant.lng], [customer.lat, customer.lng]]);
    };
    ws.onmessage = async (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg?.type === 'pos') {
          setPos({ lat: msg.lat, lng: msg.lng });
        } else if (msg?.type === 'delivered') {
          onDelivered?.();
          ws.close();
        }
      } catch {}
    };
    ws.onclose = () => {};
    ws.onerror = () => {};
    return () => {
      try { ws.close(); } catch {}
      wsRef.current = null;
    };
  }, [captainId, orderId, restaurant, customer, onDelivered]);

  return (
    <div className="w-full">
      <MapContainer
        center={[center.lat, center.lng] as LatLngExpression}
        zoom={14}
        style={{ width: '100%', height: 420 }}
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[restaurant.lat, restaurant.lng]} icon={restaurantIcon}>
          <Popup>المطعم</Popup>
        </Marker>
        <Marker position={[customer.lat, customer.lng]} icon={customerIcon}>
          <Popup>العميل</Popup>
        </Marker>
        {route.length === 2 && (
          <Polyline positions={route} pathOptions={{ color: '#8B5CF6', weight: 4 }} />
        )}
        {pos && (
          <Marker position={[pos.lat, pos.lng]} icon={captainIcon(true)}>
            <Popup>الكابتن</Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
