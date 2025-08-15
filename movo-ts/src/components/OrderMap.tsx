import React from 'react';
import MapView, { type Captain } from './MapView';

interface OrderMapProps {
  mode: 'select' | 'track';
  customerLocation?: { lat: number; lng: number };
  restaurantLocation?: { lat: number; lng: number };
  captains: Captain[];
  orderId?: number;
  onCaptainSelect?: (captainId: string) => void;
  onTrackOrder?: () => void;
}

const OrderMap: React.FC<OrderMapProps> = ({
  mode,
  customerLocation,
  restaurantLocation,
  captains,
  onCaptainSelect,
  onTrackOrder,
}) => {
  return (
    <div className="w-full mb-6">
      <div className="bg-gray-800 text-white rounded-lg p-3 mb-4 text-center">
        <span className="font-bold text-lg">
          {mode === 'select' ? 'اختيار كابتن' : 'تتبع التوصيل'}
        </span>
      </div>
      <MapView
        customerLocation={customerLocation}
        restaurantLocation={restaurantLocation}
        captains={captains}
        mode={mode}
        onCaptainSelect={onCaptainSelect}
        onTrackOrder={onTrackOrder}
      />
    </div>
  );
};

export default OrderMap;
