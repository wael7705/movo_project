import { useState } from "react";

// إعادة المكوّن: زر آمن يمنع التكرار ويعرض حالة التنفيذ لتفادي الخطأ في OrderCard
export default function UseSafeButton({ onAction, children }:{ onAction: () => Promise<void> | void; children: React.ReactNode; }) {
    const [busy, setBusy] = useState(false);
    return (
        <button onClick={async (e) => { e.stopPropagation(); if (busy) return; setBusy(true); try { await onAction(); } finally { setBusy(false); } }} aria-busy={busy}>
            {busy ? "جارٍ التنفيذ..." : children}
        </button>
    );
}


