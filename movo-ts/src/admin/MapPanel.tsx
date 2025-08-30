import { useEffect, useImperativeHandle, useMemo, useRef, forwardRef } from 'react';
import { MapContainer, TileLayer, Marker, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { captainIcon as captainIconFactory, customerIcon, restaurantIcon } from '../components/map/markers';

export type Point = { id: number | string; name: string; lat: number; lng: number; meta?: any };

export type MapPanelProps = {
  captains?: (Point & { status?: 'active' | 'busy' | 'offline'; orders_now?: number; vehicle?: string; rating?: number })[];
  restaurants?: Point[];
  customers?: Point[];
};

export type MapPanelRef = {
  highlightCaptain: (id: number | string) => void;
};

const MapPanel = forwardRef<MapPanelRef, MapPanelProps>(function MapPanel({ captains = [], restaurants = [], customers = [] }, ref) {
  const highlightedCaptainIdRef = useRef<number | string | null>(null);
  const markersRef = useRef<Record<string, L.Marker>>({});

  const center = useMemo(() => {
    const all = [...captains, ...restaurants, ...customers];
    if (all.length > 0) return { lat: all[0].lat, lng: all[0].lng };
    return { lat: 33.5138, lng: 36.2765 };
  }, [captains, restaurants, customers]);

  useImperativeHandle(ref, () => ({
    highlightCaptain: (id) => {
      highlightedCaptainIdRef.current = id;
      const mk = markersRef.current[String(id)];
      if (mk) mk.setIcon(captainIconFactory(true));
    },
  }));

  useEffect(() => {
    // reset highlight if list changes
    const id = highlightedCaptainIdRef.current;
    if (!id) return;
    const mk = markersRef.current[String(id)];
    if (mk) mk.setIcon(captainIconFactory(true));
  }, [captains]);

  return (
    <div className="w-full h-[420px] rounded-xl overflow-hidden border">
      <MapContainer center={center} zoom={13} style={{ width: '100%', height: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {restaurants.map((r) => (
          <Marker key={`rest-${r.id}`} position={[r.lat, r.lng]} icon={restaurantIcon}>
            <Tooltip>{r.name}</Tooltip>
          </Marker>
        ))}
        {customers.map((c) => (
          <Marker key={`cust-${c.id}`} position={[c.lat, c.lng]} icon={customerIcon}>
            <Tooltip>{c.name}</Tooltip>
          </Marker>
        ))}
        {captains.map((c) => (
          <Marker
            key={`cap-${c.id}`}
            position={[c.lat, c.lng]}
            icon={captainIconFactory(String(highlightedCaptainIdRef.current) === String(c.id))}
            ref={(m) => {
              if (m) markersRef.current[String(c.id)] = (m as any).leafletElement ?? (m as any);
            }}
          >
            <Tooltip>
              <div className="text-sm">
                <div className="font-semibold">{c.name}</div>
                <div>Status: {c.status ?? 'active'}</div>
                <div>Orders now: {c.orders_now ?? 0}</div>
                {typeof c.rating === 'number' && <div>Rating: {c.rating.toFixed(1)}⭐</div>}
              </div>
            </Tooltip>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
});

export default MapPanel;


