import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// حل مشكلة أيقونة الماركر الافتراضية مع Vite
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// إعداد الأيقونة الافتراضية
const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

export interface LatLng {
  lat: number;
  lng: number;
}

export interface Captain {
  id: string;
  name: string;
  coords: LatLng;
  orders?: number;
  dest?: string;
}

interface MapViewProps {
  customerLocation?: LatLng;
  restaurantLocation?: LatLng;
  captains?: Captain[];
  center?: LatLng;
  zoom?: number;
  onClose?: () => void;
  lang?: 'ar' | 'en';
}

const DEFAULT_CENTER = { lat: 33.5138, lng: 36.2765 };
const DEFAULT_ZOOM = 13;

const MapView: React.FC<MapViewProps> = ({
  customerLocation,
  restaurantLocation,
  captains = [],
  center,
  zoom,
  onClose,
  lang = 'ar',
}) => {
  useEffect(() => {
    L.Marker.prototype.options.icon = DefaultIcon;
  }, []);

  return (
    <div className="relative w-full h-[400px] rounded-lg overflow-hidden shadow mb-6">
      {onClose && (
        <button
          className="absolute top-2 left-2 z-[1000] bg-white rounded-full shadow px-2 py-1 text-gray-700 hover:bg-gray-200"
          onClick={onClose}
        >
          ×
        </button>
      )}
      <MapContainer
        center={center || DEFAULT_CENTER}
        zoom={zoom || DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {restaurantLocation && (
          <Marker position={restaurantLocation}>
            <Popup>{lang === 'ar' ? 'المطعم' : 'Restaurant'}</Popup>
          </Marker>
        )}
        {customerLocation && (
          <Marker position={customerLocation}>
            <Popup>{lang === 'ar' ? 'العميل' : 'Customer'}</Popup>
          </Marker>
        )}
        {captains.map((cap) => (
          <Marker key={cap.id} position={cap.coords}>
            <Popup>
              <div className={lang === 'ar' ? 'text-right' : 'text-left'}>
                <div className="font-bold text-purple-700 mb-1">{cap.name}</div>
                <div className="text-sm text-gray-700">{lang === 'ar' ? 'عدد الطلبات:' : 'Orders:'} {cap.orders ?? 0}</div>
                {cap.dest && <div className="text-sm text-gray-500">{lang === 'ar' ? 'الوجهة:' : 'Destination:'} {cap.dest}</div>}
              </div>
            </Popup>
          </Marker>
        ))}
        {/* دائرة حول المطعم (اختياري) */}
        {restaurantLocation && (
          <Circle center={restaurantLocation} radius={1000} pathOptions={{ color: 'purple', fillOpacity: 0.1 }} />
        )}
      </MapContainer>
    </div>
  );
};

export default MapView; 