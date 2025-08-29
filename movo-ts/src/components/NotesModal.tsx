import { useEffect, useState } from 'react';
import api from '../lib/api';

interface NotesModalProps {
  orderId: number;
  open: boolean;
  onClose: () => void;
  lang?: 'ar' | 'en';
}

export default function NotesModal({ orderId, open, onClose, lang = 'ar' }: NotesModalProps) {
  const [notes, setNotes] = useState<Array<{ note_id: number; note_text: string; created_at?: string }>>([]);
  const [insights, setInsights] = useState<string[]>([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    Promise.all([
      api.orders.notes.listByOrder(orderId).catch(() => []),
      api.orders.insights.order(orderId).then((d) => d?.insights ?? []).catch(() => []),
    ])
      .then(([ns, ins]) => {
        setNotes(Array.isArray(ns) ? ns : []);
        setInsights(Array.isArray(ins) ? ins : []);
      })
      .finally(() => setLoading(false));
  }, [open, orderId]);

  const addNote = async () => {
    if (!text.trim()) return;
    try {
      setSaving(true);
      const n = await api.orders.notes.add(orderId, text.trim());
      setNotes((prev) => [{ note_id: n.note_id, note_text: n.note_text, created_at: n.created_at }, ...prev]);
      setText('');
    } catch (e) {
      // ignore
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-black/40">
      <div className="w-[min(96vw,900px)] max-h-[80vh] overflow-auto bg-white rounded-2xl shadow-2xl border p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold">{lang === 'ar' ? 'ملاحظات الطلب' : 'Order Notes'}</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-700">✖</button>
        </div>
        {loading ? (
          <div className="text-center text-gray-500 py-10">{lang === 'ar' ? '...جاري التحميل' : 'Loading...'}</div>
        ) : (
          <div className="grid md:grid-cols-2 gap-5">
            <div>
              <div className="mb-2 text-sm text-slate-600">{lang === 'ar' ? 'أدخل ملاحظة:' : 'Add note:'}</div>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="w-full min-h-[120px] rounded-xl border p-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-amber-50 border-amber-200 text-slate-900 placeholder:text-slate-500"
                placeholder={lang === 'ar' ? 'اكتب ملاحظة للطلب...' : 'Write a note for this order...'}
              />
              <div className="mt-2 flex justify-end">
                <button
                  onClick={addNote}
                  disabled={saving || !text.trim()}
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white disabled:opacity-50 hover:bg-emerald-700"
                >
                  {lang === 'ar' ? 'حفظ الملاحظة' : 'Save Note'}
                </button>
              </div>
              <div className="mt-4">
                <div className="text-sm font-semibold mb-2">{lang === 'ar' ? 'الملاحظات السابقة' : 'Previous Notes'}</div>
                <div className="space-y-2">
                  {notes.length === 0 ? (
                    <div className="text-sm text-slate-500">{lang === 'ar' ? 'لا توجد ملاحظات' : 'No notes yet'}</div>
                  ) : (
                    notes.map((n) => (
                      <div key={n.note_id} className="rounded-xl border p-3 bg-slate-50">
                        <div className="text-sm whitespace-pre-wrap">{n.note_text}</div>
                        {n.created_at && <div className="text-xs text-slate-500 mt-1">{new Date(n.created_at).toLocaleString()}</div>}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
            <div>
              <div className="mb-2 text-sm text-slate-600">{lang === 'ar' ? 'تحليلات الذكاء الاصطناعي' : 'AI Insights'}</div>
              <div className="rounded-xl border p-3 min-h-[180px] bg-white">
                {insights.length === 0 ? (
                  <div className="text-sm text-slate-500">{lang === 'ar' ? 'لا توجد ملاحظات حرجة حالياً' : 'No critical insights'}</div>
                ) : (
                  <ul className="list-disc ms-5 text-sm space-y-1">
                    {insights.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


