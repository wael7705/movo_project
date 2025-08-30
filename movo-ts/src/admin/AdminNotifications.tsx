import { useState } from 'react';
import { sendNotify } from './api';

const tabs = ['pending','assign','processing','out_for_delivery','delivered','cancelled','issue'] as const;

export default function AdminNotifications(){
  const [tab, setTab] = useState<typeof tabs[number]>('assign');
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState<string>('');

  const send = async () => {
    setStatus('');
    if (!message.trim()) {
      setStatus('Message required');
      return;
    }
    try {
      await sendNotify(tab, message.trim());
      setStatus('Sent');
      setMessage('');
    } catch (e) {
      setStatus('Failed');
    }
  };

  return (
    <div className="max-w-xl">
      <div className="mb-3">
        <label className="block text-sm mb-1">Target tab</label>
        <select value={tab} onChange={(e)=>setTab(e.target.value as any)} className="w-full border rounded-lg px-3 py-2 bg-white">
          {tabs.map(t=> <option key={t} value={t}>{t}</option>)}
        </select>
      </div>
      <div className="mb-3">
        <label className="block text-sm mb-1">Message</label>
        <textarea value={message} onChange={(e)=>setMessage(e.target.value)} rows={4} className="w-full border rounded-lg px-3 py-2 bg-white" />
      </div>
      <button onClick={send} className="px-4 py-2 rounded-lg bg-violet-600 text-white hover:bg-violet-700">Send</button>
      {status && <div className="text-sm text-zinc-600 mt-2">{status}</div>}
    </div>
  );
}


