import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCounters } from './api';

type Counters = Record<string, number>;

const sections: { key: string; label: string; tabParam?: string }[] = [
  { key: 'pending', label: 'Pending', tabParam: 'pending' },
  { key: 'assign', label: 'Assign Captain', tabParam: 'choose_captain' },
  { key: 'processing', label: 'Processing', tabParam: 'processing' },
  { key: 'out_for_delivery', label: 'Out for Delivery', tabParam: 'out_for_delivery' },
  { key: 'delivered', label: 'Delivered', tabParam: 'delivered' },
  { key: 'cancelled', label: 'Cancelled', tabParam: 'cancelled' },
  { key: 'issue', label: 'Issue', tabParam: 'problem' },
];

const TAB_PATH: Record<string, string> = {
  pending: '/t/pending',
  assign: '/t/assign',
  processing: '/t/processing',
  out_for_delivery: '/t/out_for_delivery',
  delivered: '/t/delivered',
  cancelled: '/t/cancelled',
  issue: '/t/issue',
};

export default function AdminOrders() {
  const [counters, setCounters] = useState<Counters>({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getCounters()
      .then((c) => {
        if (mounted) setCounters(c || {});
      })
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, []);

  const openMainTab = (tab: string | undefined) => {
    if (!tab) return;
    const rev: Record<string,string> = { choose_captain:'assign', problem:'issue' };
    const key = rev[tab] ?? tab;
    const target = TAB_PATH[key] || `/t/${key}`;
    const safe = target.replace(/\/+/, '/');
    navigate(safe);
  };

  return (
    <div>
      <div className="flex flex-wrap gap-3 mb-4">
        {(Array.isArray(sections) ? sections : []).map((s) => (
          <div key={s.key} className="bg-white border rounded-xl p-4 shadow-sm min-w-[220px]">
            <div className="text-sm text-zinc-500">{s.label}</div>
            <div className="text-2xl font-bold">{counters[s.key] ?? 0}</div>
            <button
              onClick={() => openMainTab(s.tabParam)}
              className="mt-3 text-sm px-3 py-1.5 rounded-lg bg-violet-600 text-white hover:bg-violet-700"
            >
              Open
            </button>
          </div>
        ))}
      </div>
      {loading && <div className="text-zinc-500">Loading counters...</div>}
    </div>
  );
}


