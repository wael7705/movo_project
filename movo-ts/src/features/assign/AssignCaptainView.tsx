import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { restaurantIcon, customerIcon, captainIcon } from '../../components/map/markers';
import api from '../../lib/api';
import { createCaptainSocketWS } from '../../lib/socket';

type Candidate = {
  captain_id: number;
  captain_name: string;
  last_lat: number;
  last_lng: number;
  distance_km: number;
  active_orders: number;
  last_order_ids: number[];
};

export default function AssignCaptainView(props: {
  orderId: number;
  restaurant: { lat: number; lng: number };
  customer: { lat: number; lng: number };
  onWaiting?: (captainId: number) => void;
  onAssigned?: () => void;
}) {
  const { orderId, restaurant, customer, onWaiting, onAssigned } = props;
  const [cands, setCands] = useState<Candidate[]>([]);
  const [hoverId, setHoverId] = useState<number | null>(null);
  const [selectedCaptainId, setSelectedCaptainId] = useState<number | null>(null);
  const [assigningId, setAssigningId] = useState<number | null>(null);
  const hoverTimer = useRef<number | null>(null);
  const hoverWsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('Loading candidates for order', orderId);
    }
    fetch(`/api/v1/assign/orders/${orderId}/candidates`)
      .then(r => {
        if (import.meta.env.DEV) {
          console.log('Candidates response status:', r.status);
        }
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}: ${r.statusText}`);
        }
        return r.json();
      })
      .then(data => {
        if (import.meta.env.DEV) {
          console.log('Candidates loaded:', data);
        }
        setCands(data);
      })
      .catch(error => {
        if (import.meta.env.DEV) {
          console.error('Failed to load candidates:', error);
        }
        setCands([]);
      });
  }, [orderId]);

  useEffect(() => {
    // نظّف أي مؤقت/اتصال سابق
    if (hoverTimer.current) {
      clearTimeout(hoverTimer.current);
      hoverTimer.current = null;
    }
    if (hoverWsRef.current) {
      try { hoverWsRef.current.close(); } catch {}
      hoverWsRef.current = null;
    }

    if (!hoverId) return;

    // مهلة قصيرة لمنع إنشاء اتصال يُغلق قبل الاكتمال
    hoverTimer.current = window.setTimeout(() => {
      const ws = createCaptainSocketWS(hoverId);
      hoverWsRef.current = ws;
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg?.type === 'pos') {
            setCands(prev => prev.map(c => c.captain_id === hoverId ? { ...c, last_lat: msg.lat, last_lng: msg.lng } : c));
          }
        } catch {}
      };
    }, 200);

    return () => {
      if (hoverTimer.current) {
        clearTimeout(hoverTimer.current);
        hoverTimer.current = null;
      }
      if (hoverWsRef.current) {
        try { hoverWsRef.current.close(); } catch {}
        hoverWsRef.current = null;
      }
    };
  }, [hoverId]);

  const assign = async (cid: number) => {
    if (assigningId === cid) return;
    setAssigningId(cid);
    
    try {
      if (import.meta.env.DEV) {
        console.log('Assigning captain', cid, 'to order', orderId);
      }
      
      const response = await fetch(`/api/v1/assign/orders/${orderId}/assign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': (globalThis.crypto as any)?.randomUUID?.() ?? (Math.random().toString(36).slice(2) + Date.now()),
        },
        body: JSON.stringify({ captain_id: cid }),
      });
      
      if (import.meta.env.DEV) {
        console.log('Response status:', response.status);
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        if (import.meta.env.DEV) {
          console.error('Failed to assign captain:', response.status, response.statusText, errorText);
        }
        setAssigningId(null);
        return;
      }
      
      const result = await response.json();
      if (import.meta.env.DEV) {
        console.log('Assign result:', result);
      }
      
      if (result.ok) {
        if (import.meta.env.DEV) {
          console.log('Captain assigned successfully');
        }
        onWaiting?.(cid);
        setSelectedCaptainId(cid);
        
        // إنشاء WebSocket connection
        try {
          const ws = createCaptainSocketWS(cid);
          ws.onopen = () => {
            if (import.meta.env.DEV) {
              console.log('WebSocket connected for captain', cid);
            }
            ws.send(JSON.stringify({ type: 'assign', order_id: orderId }));
          };
          
          ws.onmessage = async (ev) => {
            try {
              const msg = JSON.parse(ev.data);
              if (import.meta.env.DEV) {
                console.log('WebSocket message:', msg);
              }
              if (msg?.type === 'accepted' && msg.order_id === orderId) {
                if (import.meta.env.DEV) {
                  console.log('Captain accepted order');
                }
                await api.orders.next(orderId);
                onAssigned?.();
                ws.close();
                setAssigningId(null);
              }
            } catch (error) {
              if (import.meta.env.DEV) {
                console.error('WebSocket message error:', error);
              }
            }
          };
          
          ws.onerror = (error) => {
            if (import.meta.env.DEV) {
              console.warn('WebSocket error for captain', cid);
            }
            setAssigningId(null);
          };
          
          ws.onclose = () => {
            if (import.meta.env.DEV) {
              console.log('WebSocket closed for captain', cid);
            }
          };
        } catch (wsError) {
          if (import.meta.env.DEV) {
            console.error('WebSocket creation error:', wsError);
          }
        }
        
        // timeout للتأكد من عدم تعليق الزر
        setTimeout(() => {
          if (assigningId === cid) {
            if (import.meta.env.DEV) {
              console.log('Timeout reached, resetting assigningId');
            }
            setAssigningId(null);
          }
        }, 10000);
      } else {
        if (import.meta.env.DEV) {
          console.error('Assign result not ok:', result);
        }
        setAssigningId(null);
      }
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('Assign captain error:', error);
      }
      setAssigningId(null);
    }
  };

  return (
    <div className="w-full grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 h-[460px] rounded-xl overflow-hidden border shadow">
        <MapContainer center={[restaurant.lat, restaurant.lng]} zoom={14} style={{ width: '100%', height: '100%' }} scrollWheelZoom>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Marker position={[restaurant.lat, restaurant.lng]} icon={restaurantIcon}><Popup>المطعم</Popup></Marker>
          <Marker position={[customer.lat, customer.lng]} icon={customerIcon}><Popup>العميل</Popup></Marker>
          <Polyline positions={[[restaurant.lat, restaurant.lng], [customer.lat, customer.lng]]} />
          {selectedCaptainId && (() => {
            const sc = cands.find(x => x.captain_id === selectedCaptainId);
            if (!sc) return null as any;
            return (
              <Marker position={[sc.last_lat, sc.last_lng]} icon={captainIcon(hoverId === sc.captain_id)}>
                <Popup>الكابتن المختار</Popup>
              </Marker>
            );
          })()}
          {cands.map((c) => (
            <Marker key={c.captain_id} position={[c.last_lat, c.last_lng]} icon={captainIcon(hoverId === c.captain_id)}>
              <Popup>
                <div dir="rtl">
                  <div className="font-bold text-purple-700 mb-1">{c.captain_name}</div>
                  <div className="text-sm">ID: {c.captain_id}</div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
      <div className="flex flex-col gap-3">
        {cands.map((c) => (
          <div key={c.captain_id} className="p-3 rounded-xl border shadow-sm bg-white hover:shadow-md transition cursor-pointer" onMouseEnter={() => setHoverId(c.captain_id)} onMouseLeave={() => setHoverId(null)} dir="rtl">
            <div className="font-bold text-slate-800">{c.captain_name}</div>
            <div className="text-xs text-slate-500">ID: {c.captain_id}</div>
            <button onClick={() => assign(c.captain_id)} disabled={assigningId === c.captain_id} className={`mt-2 w-full rounded-lg py-1 text-sm ${assigningId === c.captain_id ? 'bg-emerald-300 text-white cursor-not-allowed' : 'bg-emerald-600 text-white hover:bg-emerald-700'}`}>اختيار الكابتن</button>
          </div>
        ))}
      </div>
    </div>
  );
}

