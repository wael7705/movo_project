import { useEffect } from 'react';

export default function GlassToast({
  open,
  onClose,
  title,
  message,
  level = 'info',
  position = 'center',
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  message: string;
  level?: 'info' | 'success' | 'warning' | 'error';
  position?: 'left' | 'center' | 'right';
}) {
  useEffect(() => {
    if (!open) return;
    const id = setTimeout(onClose, 4500);
    return () => clearTimeout(id);
  }, [open, onClose]);

  if (!open) return null;
  const color = {
    info: 'backdrop-blur bg-white/20 border-sky-400 text-sky-900',
    success: 'backdrop-blur bg-white/20 border-emerald-400 text-emerald-900',
    warning: 'backdrop-blur bg-white/20 border-amber-400 text-amber-900',
    error: 'backdrop-blur bg-white/20 border-rose-400 text-rose-900',
  }[level];

  const justify = position === 'left' ? 'justify-start ps-4' : position === 'right' ? 'justify-end pe-4' : 'justify-center';
  return (
    <div className={`fixed top-4 inset-x-0 z-[9999] flex ${justify}`}>
      <div className={`max-w-xl w-[92%] shadow-xl border ${color} rounded-2xl px-4 py-3`}>
        <div className="font-semibold mb-1">{title}</div>
        <div className="text-sm opacity-90">{message}</div>
      </div>
    </div>
  );
}
